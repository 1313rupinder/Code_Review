import json
import os
import re
from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()

REPO_NAME = "1313rupinder/code_review_test"
MARKER = re.compile(r"<!-- copilot:([^:]+):(.+):(\d+) -->")

def posted_keys(pr):
    keys = set()
    for c in pr.get_review_comments():
        m = MARKER.search(c.body)
        if m:
            keys.add((m.group(2), int(m.group(3)), m.group(1)))
    return keys

def score(pr_number, expected):
    g = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))
    pr = g.get_repo(REPO_NAME).get_pull(pr_number)
    posted = posted_keys(pr)
    expected = {(f, line, rule) for f, line, rule in expected}
    tp = posted & expected
    fp = posted - expected
    fn = expected - posted
    precision = len(tp) / len(posted) if posted else 0
    recall = len(tp) / len(expected) if expected else 1    
    return tp, fp, fn, precision, recall

if __name__ == "__main__":
    with open("ground_truth.json", encoding="utf-8") as f:
        truth = json.load(f)

    all_tp = all_posted = all_expected = 0
    for number, expected in truth.items():
        tp, fp, fn, precision, recall = score(int(number), expected)
        print(f"PR #{number}: precision {precision:.2f}, recall {recall:.2f}")
        print("  found    :", sorted(tp))
        print("  false pos:", sorted(fp))
        print("  missed   :", sorted(fn))
        all_tp += len(tp)
        all_posted += len(tp) + len(fp)
        all_expected += len(tp) + len(fn)

    print(f"TOTAL: precision {all_tp / all_posted:.2f}, recall {all_tp / all_expected:.2f}")