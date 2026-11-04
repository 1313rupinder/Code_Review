from pipeline import drop_skipped, is_test_file


def finding(rule, file="app.py"):
    return {"rule": rule, "file": file}


def test_is_test_file_recognizes_common_layouts():
    assert is_test_file("tests/foo.py")
    assert is_test_file("pkg/tests/foo.py")
    assert is_test_file("test_foo.py")
    assert is_test_file("pkg/foo_test.py")
    assert is_test_file("conftest.py")


def test_is_test_file_rejects_normal_files():
    assert not is_test_file("app.py")
    assert not is_test_file("pkg/contest.py")
    assert not is_test_file("pkg/latest_notes.py")
    assert not is_test_file("attestation.py")


def test_assert_noise_is_skipped_only_in_test_files():
    findings = [finding("B101", "tests/a_test.py"), finding("B101", "app.py")]
    assert [f["file"] for f in drop_skipped(findings)] == ["app.py"]


def test_constant_subprocess_warnings_are_skipped_but_shell_true_is_kept():
    findings = [finding("B603"), finding("B607"), finding("B602")]
    assert [f["rule"] for f in drop_skipped(findings)] == ["B602"]