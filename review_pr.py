import json
import os
import subprocess
import requests
from dotenv import load_dotenv
from github import Github, Auth
from unidiff import PatchSet
from filter_comments import clean_comments
from filter_findings import get_added_lines, keep_new_findings
from review_finding import review_finding
from run_checks import run_ruff, run_bandit
from settings import SKIP_RULES

load_dotenv()

TOKEN = os.environ["GITHUB_TOKEN"]
REPO_NAME = os.environ.get("GITHUB_REPOSITORY", "1313rupinder/code_review_test")
REPO_DIR = os.environ.get("GITHUB_WORKSPACE", "D:/code_review_test")
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() != "false"

def get_pr_number():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path:
        with open(event_path, encoding="utf-8") as f:
            return json.load(f)["pull_request"]["number"]
    return int(os.environ.get("PR_NUMBER", "1"))

def fetch_pr_diff(pr_number):
    url = f"https://api.github.com/repos/{REPO_NAME}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def get_local_head_sha():
    result = subprocess.run(
        ["git", "-C", REPO_DIR, "rev-parse", "HEAD"],
        capture_output=True, text=True,
    )
    return result.stdout.strip()

def marker_for(finding):
    return f"<!-- copilot:{finding['rule']}:{finding['file']}:{finding['start_line']} -->"

def main():
    pr_number = get_pr_number()
    g = Github(auth=Auth.Token(TOKEN))
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(pr_number)
    head_sha = pr.head.sha

    if get_local_head_sha() != head_sha:
        raise SystemExit("Checked-out code is not the PR head commit. Stopping.")

    diff_text = fetch_pr_diff(pr_number)
    diff_path = os.path.abspath("pr.diff")
    with open(diff_path, "w", encoding="utf-8", newline="") as f:
        f.write(diff_text)
    added = get_added_lines(diff_path)

    os.chdir(REPO_DIR)
    findings = []
    for file in PatchSet(diff_text):
        if file.path.endswith(".py") and not file.is_removed_file:
            findings += run_ruff(file.path) + run_bandit(file.path)
    kept = keep_new_findings(findings, added)
    kept = [f for f in kept if f["rule"] not in SKIP_RULES]

    existing = " ".join(c.body for c in pr.get_review_comments())
    fresh = [f for f in kept if marker_for(f) not in existing]
    print(f"PR #{pr_number}: {len(findings)} findings, {len(kept)} on changed lines, {len(fresh)} not yet posted")

    comments = clean_comments([review_finding(f) for f in fresh])
    to_post = []
    for c in comments:
        marker = f"<!-- copilot:{c['rule']}:{c['file']}:{c['line']} -->"
        body = f"{marker}\n**{c['severity'].upper()}** ({c['rule']}): {c['comment']}"
        print("Comment:", c["file"], c["line"], "-", c["comment"])
        to_post.append({"path": c["file"], "line": c["line"], "side": "RIGHT", "body": body})

    if DRY_RUN:
        print("Dry run: nothing posted.")
    elif to_post:
        pr.create_review(
            commit=repo.get_commit(head_sha),
            body="Automated first-pass review.",
            event="COMMENT",
            comments=to_post,
        )
        print("Posted", len(to_post), "comment(s).")
    else:
        print("Nothing new to post.")

if __name__ == "__main__":
    main()