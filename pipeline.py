from unidiff import PatchSet

from filter_findings import keep_new_findings
from run_checks import run_ruff, run_bandit
from settings import SKIP_RULES


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


def drop_skipped(findings):
    return [f for f in findings if f["rule"] not in SKIP_RULES]


def find_new_findings(added):
    findings = []
    for path in sorted(added):
        findings += run_ruff(path) + run_bandit(path)
    kept = drop_skipped(keep_new_findings(findings, added))
    return findings, kept