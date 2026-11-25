from build_prompt import get_code_context

def test_reads_non_english_text(tmp_path):
    path = tmp_path / "a.py"
    path.write_text('name = "नमस्ते"\nx = 1\n', encoding="utf-8")
    assert "नमस्ते" in get_code_context(str(path), 1, 1)

def test_bad_bytes_do_not_crash(tmp_path):
    path = tmp_path / "b.py"
    path.write_bytes(b"x = 1\n\xff\xfe\ny = 2\n")
    assert "x = 1" in get_code_context(str(path), 1, 1)