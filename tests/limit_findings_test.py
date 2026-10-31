from pipeline import limit_findings

def finding(source, file, line):
    return {"source": source, "file": file, "start_line": line}

def test_everything_is_kept_under_the_limit():
    items = [finding("ruff", "a.py", 2), finding("bandit", "a.py", 1)]
    selected, skipped = limit_findings(items, 5)
    assert len(selected) == 2
    assert skipped == 0

def test_security_findings_are_kept_first_when_over_the_limit():
    items = [finding("ruff", "a.py", 1), finding("ruff", "a.py", 2), finding("bandit", "b.py", 9)]
    selected, skipped = limit_findings(items, 2)
    assert selected[0]["source"] == "bandit"
    assert len(selected) == 2
    assert skipped == 1

def test_empty_input_gives_empty_output():
    assert limit_findings([], 5) == ([], 0)