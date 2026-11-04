from unidiff import PatchSet
from filter_findings import keep_new_findings
from run_checks import run_ruff, run_bandit
from settings import SKIP_RULES, SKIP_RULES_IN_TESTS

def added_from_diff(diff_text):
    added = {}
    for file in PatchSet(diff_text):
        if file.is_removed_file or not file.path.endswith(".py"):
            continue
        lines = set()
        for hunk in file:
            for line in hunk:
                if line.is_added:
                    lines.add(line.target_line_no)
        added[file.path] = lines
    return added

def is_test_file(path):
    parts = path.split("/")
    name = parts[-1]
    return (
        "tests" in parts[:-1]
        or "test" in parts[:-1]
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name == "conftest.py"
    )

def drop_skipped(findings):
    kept = []
    for f in findings:
        if f["rule"] in SKIP_RULES:
            continue
        if f["rule"] in SKIP_RULES_IN_TESTS and is_test_file(f["file"]):
            continue
        kept.append(f)
    return kept

def find_new_findings(added):
    findings = []
    for path in sorted(added):
        findings += run_ruff(path) + run_bandit(path)
    kept = drop_skipped(keep_new_findings(findings, added))
    return findings, kept

def limit_findings(findings, max_calls):
    ranked = sorted(findings, key=lambda f: (f["source"] != "bandit", f["file"], f["start_line"]))
    return ranked[:max_calls], max(0, len(ranked) - max_calls)