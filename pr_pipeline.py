import os
import subprocess
import requests
from dotenv import load_dotenv
from github import Github, Auth
from unidiff import PatchSet
from filter_findings import get_added_lines, keep_new_findings
from run_checks import run_ruff, run_bandit

load_dotenv()

REPO_NAME = "1313rupinder/code_review_test"
PR_NUMBER = 1
REPO_DIR = "D:/code_review_test"
TOKEN = os.environ["GITHUB_TOKEN"]

def fetch_pr_diff():
    url = f"https://api.github.com/repos/{REPO_NAME}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def get_pr_head_sha():
    g = Github(auth=Auth.Token(TOKEN))
    return g.get_repo(REPO_NAME).get_pull(PR_NUMBER).head.sha

def get_local_head_sha():
    result = subprocess.run(
        ["git", "-C", REPO_DIR, "rev-parse", "HEAD"],
        capture_output=True, text=True,
    )
    return result.stdout.strip()

if __name__ == "__main__":
    pr_sha = get_pr_head_sha()
    local_sha = get_local_head_sha()
    if pr_sha != local_sha:
        raise SystemExit(f"Local code {local_sha[:7]} is not the PR code {pr_sha[:7]}. Stopping.")

    diff_text = fetch_pr_diff()
    diff_path = os.path.abspath("pr.diff")
    with open(diff_path, "w", encoding="utf-8", newline="") as f:
        f.write(diff_text)

    added = get_added_lines(diff_path)
    print("Added lines per file:", added)

    os.chdir(REPO_DIR)

    findings = []
    for file in PatchSet(diff_text):
        if file.path.endswith(".py") and not file.is_removed_file:
            findings += run_ruff(file.path) + run_bandit(file.path)

    kept = keep_new_findings(findings, added)
    print("Before filter:", len(findings))
    print("After filter:", len(kept))
    for f in kept:
        print(f'{f["file"]}:{f["start_line"]}-{f["end_line"]}  [{f["source"]}:{f["rule"]}]  {f["message"]}')