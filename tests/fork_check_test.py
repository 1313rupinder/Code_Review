from types import SimpleNamespace
from pipeline import is_fork

def make_pr(head_name, base_name):
    head = SimpleNamespace(repo=SimpleNamespace(full_name=head_name))
    base = SimpleNamespace(repo=SimpleNamespace(full_name=base_name))
    return SimpleNamespace(head=head, base=base)

def test_same_repo_is_not_fork():
    assert not is_fork(make_pr("a/b", "a/b"))

def test_other_repo_is_fork():
    assert is_fork(make_pr("x/b", "a/b"))

def test_deleted_fork_is_fork():
    pr = SimpleNamespace(head=SimpleNamespace(repo=None), base=SimpleNamespace(repo=SimpleNamespace(full_name="a/b")))
    assert is_fork(pr)