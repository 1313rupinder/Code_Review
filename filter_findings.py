from unidiff import PatchSet
from run_checks import run_ruff, run_bandit

def get_added_lines(diff_path):
    with open(diff_path) as f:
        patch = PatchSet(f.read())
    added = {}
    for file in patch:
        lines = set()
        for hunk in file:
            for line in hunk:
                if line.is_added:
                    lines.add(line.target_line_no)
        added[file.path] = lines
    return added

def keep_new_findings(findings, added):
    kept = []
    for f in findings:
        changed = added.get(f["file"], set())
        finding_lines = set(range(f["start_line"], f["end_line"] + 1))
        if finding_lines & changed:
            kept.append(f)
    return kept

if __name__ == "__main__":
    target = "samples/app.py"
    added = get_added_lines("sample.diff")
    findings = run_ruff(target) + run_bandit(target)
    kept = keep_new_findings(findings, added)
    print("Before filter:", len(findings))
    print("After filter:", len(kept))
    for f in kept:
        print(f'{f["file"]}:{f["start_line"]}-{f["end_line"]}  [{f["source"]}:{f["rule"]}]  {f["message"]}')