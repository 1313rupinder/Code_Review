from style_guide import parse_guide, rules_for

GUIDE = """# Team guide

## Use parameterized queries
rules: B608
Pass values as parameters. Never build SQL with f-strings.

## No secrets in code
rules: B105, b106
Read credentials from environment variables.

## Prefer logging over print
Use the logging module in services.
"""

def test_parse_guide_reads_title_codes_and_text():
    rules = parse_guide(GUIDE)
    assert [r["title"] for r in rules] == [
        "Use parameterized queries",
        "No secrets in code",
        "Prefer logging over print",
    ]
    assert rules[0]["codes"] == {"B608"}
    assert rules[1]["codes"] == {"B105", "B106"}
    assert rules[0]["text"] == "Pass values as parameters. Never build SQL with f-strings."

def test_rule_without_codes_has_an_empty_set():
    assert parse_guide(GUIDE)[2]["codes"] == set()

def test_rules_for_matches_by_rule_code():
    rules = parse_guide(GUIDE)
    found = rules_for({"rule": "B608"}, rules)
    assert [r["title"] for r in found] == ["Use parameterized queries"]
    assert rules_for({"rule": "F401"}, rules) == []

def test_empty_guide_gives_no_rules():
    assert parse_guide("") == []