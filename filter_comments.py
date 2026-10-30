SEVERITY_RANK = {"high": 3, "medium": 2, "low": 1}
MAX_COMMENTS = 10
MIN_SEVERITY = "low"

def clean_comments(comments, max_comments=MAX_COMMENTS, min_severity=MIN_SEVERITY):
    best = {}
    for c in comments:
        if c is None:
            continue
        if SEVERITY_RANK[c["severity"]] < SEVERITY_RANK[min_severity]:
            continue
        key = (c["file"], c["line"])
        if key not in best or SEVERITY_RANK[c["severity"]] > SEVERITY_RANK[best[key]["severity"]]:
            best[key] = c
    ranked = sorted(best.values(), key=lambda c: SEVERITY_RANK[c["severity"]], reverse=True)
    return ranked[:max_comments]

if __name__ == "__main__":
    fake = [
        None,
        {"file": "a.py", "line": 3, "rule": "F841", "severity": "low", "comment": "unused var"},
        {"file": "a.py", "line": 3, "rule": "B105", "severity": "high", "comment": "hardcoded password"},
        {"file": "a.py", "line": 9, "rule": "F401", "severity": "medium", "comment": "unused import"},
        {"file": "b.py", "line": 1, "rule": "F841", "severity": "low", "comment": "unused var"},
    ]
    for c in clean_comments(fake, max_comments=2):
        print(c["file"], c["line"], c["severity"], c["rule"])