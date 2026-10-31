import review_finding as rf
import settings

def make_finding(rule):
    return {
        "file": "app.py", "start_line": 2, "end_line": 2, "source": "bandit",
        "rule": rule, "message": "Possible hardcoded password: 'hunter2'",
    }

def test_parse_reply_accepts_valid_json():
    reply = rf.parse_reply('{"severity": "high", "comment": " Fix it. "}')
    assert reply == {"severity": "high", "comment": "Fix it."}

def test_parse_reply_accepts_fenced_json():
    text = '```json\n{"severity": "low", "comment": "ok"}\n```'
    assert rf.parse_reply(text) == {"severity": "low", "comment": "ok"}

def test_parse_reply_rejects_bad_replies():
    assert rf.parse_reply(None) is None
    assert rf.parse_reply("not json") is None
    assert rf.parse_reply('["a"]') is None
    assert rf.parse_reply('{"severity": "urgent", "comment": "x"}') is None
    assert rf.parse_reply('{"severity": "low", "comment": "  "}') is None

def test_redact_hides_every_occurrence():
    assert rf.redact("a hunter2 b hunter2", ["hunter2"]) == "a <redacted> b <redacted>"

def test_get_secret_values_finds_long_quoted_strings_only(tmp_path):
    path = tmp_path / "x.py"
    path.write_text('x = 1\npassword = "hunter2"\nok = "ab"\n')
    assert rf.get_secret_values(str(path), 2, 3) == ["hunter2"]

def test_review_finding_never_sends_secret_to_model(tmp_path, monkeypatch):
    (tmp_path / "app.py").write_text('x = 1\npassword = "hunter2"\ny = 2\n')
    monkeypatch.chdir(tmp_path)
    seen = []

    def fake_model(prompt):
        seen.append(prompt)
        return '{"severity": "high", "comment": "The value hunter2 is hardcoded."}'

    monkeypatch.setattr(rf, "ask_model", fake_model)
    result = rf.review_finding(make_finding("B105"))
    assert "hunter2" not in seen[0]
    assert "hunter2" not in result["comment"]
    assert result["line"] == 2
    assert result["rule"] == "B105"

def test_review_finding_survives_model_failure(tmp_path, monkeypatch):
    (tmp_path / "app.py").write_text('x = 1\npassword = "hunter2"\n')
    monkeypatch.chdir(tmp_path)

    def broken_model(prompt):
        raise RuntimeError("network down")

    monkeypatch.setattr(rf, "ask_model", broken_model)
    assert rf.review_finding(make_finding("B105")) is None

def test_client_gets_timeout_and_retries(monkeypatch):
    seen = {}

    class FakeGroq:
        def __init__(self, **kwargs):
            seen.update(kwargs)

    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    monkeypatch.setattr(rf, "Groq", FakeGroq)
    rf.get_client.cache_clear()
    rf.get_client()
    rf.get_client.cache_clear()
    assert seen["timeout"] == settings.MODEL_TIMEOUT_SECONDS
    assert seen["max_retries"] == settings.MODEL_MAX_RETRIES