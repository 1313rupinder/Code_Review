import os
from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()
g = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))
repo = g.get_repo("1313rupinder/code_review_test")
pr = repo.get_pull(1)

print(pr.title)
print(pr.head.sha)
for f in pr.get_files():
    print(f.filename, f.additions, f.deletions)