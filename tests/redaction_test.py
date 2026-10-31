import review_finding as rf
from redaction import redact_secret_like

def test_assignment_with_secret_name_is_redacted():
    out = redact_secret_like('db_password = "hunter2"')
    assert out == 'db_password = "<redacted>"'

def test_api_key_and_dict_styles_are_redacted():
    assert "abcdef123456" not in redact_secret_like('API_KEY = "abcdef123456"')
    assert "abcdef123456" not in redact_secret_like('{"token": "abcdef123456"}')
    assert "abcdef123456" not in redact_secret_like("client(secret='abcdef123456')")

def test_known_token_formats_are_redacted():
    github = "gh" + "p_" + "a" * 30
    groq = "gs" + "k_" + "b" * 30
    out = redact_secret_like(f"see {github} and {groq} here")
    assert out == "see <redacted> and <redacted> here"

def test_normal_code_is_left_alone():
    code = 'token = os.environ["TOKEN"]\nif password == secret:\n    count = "hello world"\n'
    assert redact_secret_like(code) == code

def test_short_values_are_a_known_gap():
    assert redact_secret_like('password = "ab"') == 'password = "ab"'

def test_secret_on_neighbor_line_is_not_sent_to_model(tmp_path, monkeypatch):
    (tmp_path / "app.py").write_text('API_KEY = "sk-live-0123456789abcdef"\nx = 1\nquery = "a" + name\n')
    monkeypatch.chdir(tmp_path)
    seen = []

    def fake_model(prompt):
        seen.append(prompt)
        return '{"severity": "high", "comment": "Use a parameterized query."}'

    monkeypatch.setattr(rf, "ask_model", fake_model)
    finding = {
        "file": "app.py", "start_line": 3, "end_line": 3, "source": "bandit",
        "rule": "B608", "message": "Possible SQL injection vector through string-based query construction.",
    }
    assert rf.review_finding(finding) is not None
    assert "sk-live-0123456789abcdef" not in seen[0]