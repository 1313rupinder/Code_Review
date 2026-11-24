import re
from github import GithubException

def parse_guide(text):
    rules = []
    for block in re.split(r"(?m)^## ", text)[1:]:
        title, _, body = block.partition("\n")
        codes = set()
        lines = []
        for line in body.strip().splitlines():
            if line.lower().startswith("rules:"):
                names = line.split(":", 1)[1].split(",")
                codes = {n.strip().upper() for n in names if n.strip()}
            else:
                lines.append(line)
        rules.append({"title": title.strip(), "codes": codes, "text": "\n".join(lines).strip()})
    return rules

def rules_for(finding, rules):
    return [r for r in rules if finding["rule"] in r["codes"]]

def load_guide_text(repo, ref):
    try:
        item = repo.get_contents("STYLE_GUIDE.md", ref=ref)
    except GithubException as error:
        if error.status == 404:
            return ""
        raise
    return item.decoded_content.decode("utf-8")