from filter_comments import clean_comments
import settings

def make(file, line, rule, severity):
    return {"file": file, "line": line, "rule": rule, "severity": severity, "comment": "x"}

def test_failed_replies_are_skipped():
    assert clean_comments([None, None]) == []

def test_same_line_different_rules_both_survive():
    comments = [make("a.py", 3, "F841", "low"), make("a.py", 3, "B105", "high")]
    assert len(clean_comments(comments)) == 2

def test_same_rule_same_line_keeps_higher_severity():
    comments = [make("a.py", 3, "B105", "low"), make("a.py", 3, "B105", "high")]
    result = clean_comments(comments)
    assert len(result) == 1
    assert result[0]["severity"] == "high"

def test_highest_severity_first_and_cap_applies():
    comments = [
        make("a.py", 1, "F401", "low"),
        make("a.py", 2, "B105", "high"),
        make("a.py", 3, "B113", "medium"),
    ]
    result = clean_comments(comments, max_comments=2)
    assert [c["severity"] for c in result] == ["high", "medium"]

def test_settings_skip_import_noise():
    assert {"B403", "B404"} <= settings.SKIP_RULES  