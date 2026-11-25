# Code Review Copilot (Part 1: Code Reviewer)

Reads a GitHub pull request, finds problems only on the changed lines with Ruff and Bandit, and posts short inline comments written by an LLM (Groq). Team rules from `STYLE_GUIDE.md` on the base branch shape the wording.

## How it works
1. A GitHub Actions workflow runs on every PR.
2. The diff gives the changed lines (unidiff).
3. Ruff and Bandit find problems; only those on changed lines are kept.
4. Secret-looking values are hidden, then the LLM explains each finding.
5. One comment per rule per line is posted. Comments already posted are skipped.

## Results (6 fair tests, answer key committed before the code)
| PR | What it tested | Precision | Recall |
|---|---|---|---|
| 3 | bad code only | 0.89 | 1.00 |
| 4 | bad code + logic bug | 1.00 | 0.83 |
| 5 | bad and safe code mixed | 0.60 | 0.75 |
| 6 | same, after skip rules | 1.00 | 0.83 |
| 7 | team rules (generic text) | 1.00 | 1.00 |
| 8 | team rules (specific text) | 1.00 | 1.00 |

PR 7 key: line numbers were copied wrong and fixed in a later commit; the file was unchanged. PRs 1 and 2 were development runs and are not counted.
Team-rule test: with specific rules the comments changed from `os.getenv`, `%s`, `timeout=10` (PR 7) to `os.environ`, `:name`, `timeout=5` (PR 8).

## Known limits
- Python only. Small files, textbook problems: a pipeline check, not a general accuracy claim.
- The model explains what the tools find. Logic bugs are never found.
- Some advice can be weak or wrong. A human must read the comments.
- The code around each finding is sent to Groq. Redaction has gaps, so this is not safe for private company code.
- PRs from forks fail (GitHub gives them no secrets).
- Only added lines are checked. B603, B607, B403, B404 are skipped everywhere.
- Team rules only cover codes listed in `rules:` lines.