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