from review_finding import safe_message

def test_safe_message_hides_password(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text('secret = "admin123"\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    finding = {
        "file": "a.py",
        "start_line": 1,
        "end_line": 1,
        "rule": "B105",
        "message": "Possible hardcoded password: 'admin123'",
    }
    assert "admin123" not in safe_message(finding)

def test_safe_message_keeps_other_rules(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    finding = {
        "file": "a.py",
        "start_line": 1,
        "end_line": 1,
        "rule": "F401",
        "message": "`os` imported but unused",
    }
    assert safe_message(finding) == "`os` imported but unused"