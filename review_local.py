import argparse
import os
import subprocess
from filter_comments import clean_comments
from pipeline import added_from_diff, find_new_findings
from settings import SKIP_DIRS, MAX_MODEL_CALLS, MAX_COMMENTS

def run_git(repo, *args):
    result = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout

def all_lines(repo, rel_path):
    with open(os.path.join(repo, rel_path), encoding="utf-8", errors="replace") as f:
        return set(range(1, sum(1 for _ in f) + 1))

def git_mode(repo, base):
    diff_text = run_git(repo, "diff", base, "--relative", "--no-color")
    added = added_from_diff(diff_text)
    for rel in run_git(repo, "ls-files", "--others", "--exclude-standard").splitlines():
        if rel.endswith(".py"):
            added[rel] = all_lines(repo, rel)
    return added

def files_mode(repo, paths):
    added = {}
    for p in paths:
        full = os.path.abspath(os.path.join(repo, p))
        found = []
        if os.path.isdir(full):
            for folder, dirs, names in os.walk(full):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                found += [os.path.join(folder, n) for n in names if n.endswith(".py")]
        elif os.path.isfile(full) and full.endswith(".py"):
            found.append(full)
        else:
            print("Skipping (not a .py file or a folder):", p)
        for path in found:
            rel = os.path.relpath(path, repo).replace(os.sep, "/")
            if rel.startswith(".."):
                print("Skipping (outside the repo folder):", path)
                continue
            added[rel] = all_lines(repo, rel)
    return added

def main():
    parser = argparse.ArgumentParser(description="Review local Python code without GitHub.")
    parser.add_argument("paths", nargs="*", help="files or folders to review in full; leave empty to review git changes")
    parser.add_argument("--repo", default=".", help="folder to work in (default: current folder)")
    parser.add_argument("--base", default="HEAD", help="git mode: compare against this commit or branch")
    parser.add_argument("--max", type=int, default=MAX_COMMENTS, help="most comments to show")
    parser.add_argument("--no-llm", action="store_true", help="show tool findings only, no model call")
    parser.add_argument("--report", help="also write the comments to this Markdown file")
    parser.add_argument("--force", action="store_true", help="allow more than 25 model calls")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    report_path = os.path.abspath(args.report) if args.report else None
    os.chdir(repo)

    added = files_mode(repo, args.paths) if args.paths else git_mode(repo, args.base)
    if not added:
        print("No Python files to review.")
        return

    findings, kept = find_new_findings(added)
    print(f"{len(added)} file(s), {len(findings)} findings, {len(kept)} on changed lines")

    if args.no_llm:
        for f in sorted(kept, key=lambda f: (f["file"], f["start_line"])):
            print(f'{f["file"]}:{f["start_line"]}  [{f["source"]}:{f["rule"]}]  {f["message"]}')
        return

    if len(kept) > MAX_MODEL_CALLS and not args.force:
        raise SystemExit(f"{len(kept)} findings need {len(kept)} model calls (limit {MAX_MODEL_CALLS}). Narrow the paths, or add --force.")

    from review_finding import review_finding

    print("Note: the code around each finding is sent to the Groq API.")
    comments = clean_comments([review_finding(f) for f in kept], max_comments=args.max)
    if not comments:
        print("No comments.")
        return

    comments = sorted(comments, key=lambda c: (c["file"], c["line"]))
    for c in comments:
        print(f'{c["file"]}:{c["line"]}  [{c["severity"].upper()}] ({c["rule"]}) {c["comment"]}')

    if report_path:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Local code review\n\n")
            for c in comments:
                f.write(f'- **{c["severity"].upper()}** `{c["file"]}:{c["line"]}` ({c["rule"]}): {c["comment"]}\n')
        print("Report written to", report_path)

if __name__ == "__main__":
    main()