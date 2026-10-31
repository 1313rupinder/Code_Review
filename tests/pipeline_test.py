from pipeline import added_from_diff, drop_skipped, find_new_findings

MODIFIED = "\n".join([
    "diff --git a/app.py b/app.py",
    "--- a/app.py",
    "+++ b/app.py",
    "@@ -1,2 +1,3 @@",
    " import os",
    "+import sys",
    " print('x')",
    "",
])

NOT_PYTHON = "\n".join([
    "diff --git a/notes.md b/notes.md",
    "--- a/notes.md",
    "+++ b/notes.md",
    "@@ -1,1 +1,2 @@",
    " title",
    "+more text",
    "",
])

DELETED = "\n".join([
    "diff --git a/old.py b/old.py",
    "deleted file mode 100644",
    "--- a/old.py",
    "+++ /dev/null",
    "@@ -1,1 +0,0 @@",
    "-x = 1",
    "",
])


def test_added_from_diff_collects_added_line_numbers():
    assert added_from_diff(MODIFIED) == {"app.py": {2}}


def test_added_from_diff_skips_non_python_and_deleted_files():
    assert added_from_diff(NOT_PYTHON + DELETED) == {}


def test_drop_skipped_removes_import_noise():
    findings = [{"rule": "B404"}, {"rule": "B602"}, {"rule": "B403"}]
    assert [f["rule"] for f in drop_skipped(findings)] == ["B602"]


def test_find_new_findings_ignores_old_lines(tmp_path, monkeypatch):
    code = 'import os\n\ndef f():\n    secret = "admin123"\n    return 1\n'
    (tmp_path / "app.py").write_text(code)
    monkeypatch.chdir(tmp_path)
    findings, kept = find_new_findings({"app.py": {4}})
    assert "F401" in {f["rule"] for f in findings}
    assert "F401" not in {f["rule"] for f in kept}
    assert "B105" in {f["rule"] for f in kept}