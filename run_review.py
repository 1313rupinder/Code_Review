import os
from github import Github, Auth
from unidiff import PatchSet
from pr_pipeline import (
    REPO_NAME, PR_NUMBER, REPO_DIR, TOKEN,
    fetch_pr_diff, get_pr_head_sha, get_local_head_sha,
)
from filter_findings import get_added_lines, keep_new_findings
from filter_comments import clean_comments
from review_finding import review_finding
from run_checks import run_ruff, run_bandit

DRY_RUN = False

def make_body(c):
    marker = f"<!-- copilot:{c['rule']}:{c['file']}:{c['line']} -->"
    body = f"{marker}\n**{c['severity'].upper()}** ({c['rule']}): {c['comment']}"
    return marker, body

if __name__ == "__main__":
    pr_sha = get_pr_head_sha()
    if pr_sha != get_local_head_sha():
        raise SystemExit("Local code is not the PR code. Stopping.")

    diff_text = fetch_pr_diff()
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

    comments = clean_comments([review_finding(f) for f in kept])

    g = Github(auth=Auth.Token(TOKEN))
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(PR_NUMBER)
    existing = [c.body for c in pr.get_review_comments()]

    to_post = []
    for c in comments:
        marker, body = make_body(c)
        if any(marker in e for e in existing):
            print("Skip (already posted):", c["file"], c["line"], c["rule"])
            continue
        print("Would post:", c["file"], c["line"], "-", body.split("\n", 1)[1])
        to_post.append({"path": c["file"], "line": c["line"], "side": "RIGHT", "body": body})

    if DRY_RUN:
        print("Dry run: nothing posted. Set DRY_RUN = False to post.")
    elif to_post:
        pr.create_review(
            commit=repo.get_commit(pr_sha),
            body="Automated first-pass review.",
            event="COMMENT",
            comments=to_post,
        )
        print("Posted", len(to_post), "comment(s).")
    else:
        print("Nothing new to post.")