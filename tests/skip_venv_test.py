from review_local import files_mode

def test_skips_folder_with_pyvenv_cfg(tmp_path):
    (tmp_path / "myenv").mkdir()
    (tmp_path / "myenv" / "pyvenv.cfg").write_text("home = x\n")
    (tmp_path / "myenv" / "lib.py").write_text("x = 1\n")
    (tmp_path / "app.py").write_text("y = 2\n")
    found = files_mode(str(tmp_path), ["."])
    assert "app.py" in found
    assert "myenv/lib.py" not in found