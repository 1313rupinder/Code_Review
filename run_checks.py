import json
import subprocess
import sys
from pathlib import Path


def clean_path(p):
    return Path(p).resolve().relative_to(Path.cwd().resolve()).as_posix()


def run_ruff(target):
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--isolated", "--select", "F",
         "--output-format", "json", target],
        capture_output=True, text=True,
    )
    findings = []
    for item in json.loads(result.stdout):
        findings.append({
            "file": clean_path(item["filename"]),
            "start_line": item["location"]["row"],
            "end_line": item["end_location"]["row"],
            "source": "ruff",
            "rule": item["code"],
            "message": item["message"],
        })
    return findings


def run_bandit(target):
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-q", "-f", "json", target],
        capture_output=True, text=True,
    )
    findings = []
    for item in json.loads(result.stdout)["results"]:
        findings.append({
            "file": clean_path(item["filename"]),
            "start_line": item["line_number"],
            "end_line": max(item["line_range"], default=item["line_number"]),
            "source": "bandit",
            "rule": item["test_id"],
            "message": item["issue_text"],
        })
    return findings


if __name__ == "__main__":
    target = "samples/app.py"
    findings = run_ruff(target) + run_bandit(target)
    for f in findings:
        print(f'{f["file"]}:{f["start_line"]}-{f["end_line"]}  [{f["source"]}:{f["rule"]}]  {f["message"]}')