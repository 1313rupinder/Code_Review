from filter_findings import get_added_lines, keep_new_findings
from run_checks import run_ruff, run_bandit


def get_code_context(file_path, start_line, end_line, padding=3):
    with open(file_path) as f:
        lines = f.read().splitlines()
    first = max(1, start_line - padding)
    last = min(len(lines), end_line + padding)
    numbered = []
    for number in range(first, last + 1):
        numbered.append(f"{number}: {lines[number - 1]}")
    return "\n".join(numbered)


def build_prompt(finding, context):
    return (
        "You are a code reviewer. Write a short review comment for the finding below.\n"
        "Rules: at most 2 sentences. Explain the problem and suggest a fix. "
        "Do not mention anything outside the finding.\n\n"
        f"Tool: {finding['source']} ({finding['rule']})\n"
        f"Message: {finding['message']}\n"
        f"Lines: {finding['start_line']}-{finding['end_line']}\n\n"
        f"Code:\n{context}\n"
    )


if __name__ == "__main__":
    target = "samples/app.py"
    added = get_added_lines("sample.diff")
    findings = run_ruff(target) + run_bandit(target)
    kept = keep_new_findings(findings, added)
    for f in kept:
        context = get_code_context(f["file"], f["start_line"], f["end_line"])
        print(build_prompt(f, context))
        print("-" * 40)