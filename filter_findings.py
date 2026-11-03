def keep_new_findings(findings, added):
    kept = []
    for f in findings:
        changed = added.get(f["file"], set())
        finding_lines = set(range(f["start_line"], f["end_line"] + 1))
        if finding_lines & changed:
            kept.append(f)
    return kept