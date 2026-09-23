import os
from pathlib import Path

import kattistools.checkers.check_data as check_data
from kattistools.check_problem import run_checkers
from kattistools.args import Args

def size_messages(path: Path):
    args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    all_messages = []
    def collect_error(p, e):
        for msgs in e.values():
            all_messages.extend(msgs)
    run_checkers(args, [check_data.CheckData], [], [], collect_error)
    return [m for m in all_messages if 'Kattis refuses to install' in m]

def make_problem(path: Path, contents: list[bytes]):
    (path / "data" / "secret").mkdir(parents=True)
    (path / "problem.yaml").write_text("name: x\n")
    for i, content in enumerate(contents):
        (path / "data" / "secret" / f"{i}.in").write_bytes(content)
        (path / "data" / "secret" / f"{i}.ans").write_bytes(b"1\n")

MIB = 1024 * 1024

def test_testdata_size(tmp_path, monkeypatch):
    monkeypatch.setattr(check_data, "MAX_TESTDATA_MIB", 1)

    small = tmp_path / "small"
    make_problem(small, [b"a" * (MIB // 2)])
    assert size_messages(small) == []

    big = tmp_path / "big"
    make_problem(big, [b"a" * (MIB // 2), b"b" * (MIB // 2), b"c" * (MIB // 2)])
    msgs = size_messages(big)
    assert len(msgs) == 1
    assert "Test data is 1.5 MiB" in msgs[0]

    # Kattis only stores identical files once, but we only deduplicate symlinks
    duplicated = tmp_path / "duplicated"
    make_problem(duplicated, [b"a" * (MIB // 2)] * 3)
    assert len(size_messages(duplicated)) == 1

    # Symlinked test cases count, but deduplicate
    symlinked = tmp_path / "symlinked"
    make_problem(symlinked, [b"a" * (MIB // 4), b"b" * (MIB // 4)])
    (symlinked / "data" / "secret" / "group1").mkdir()
    os.symlink("../0.in", symlinked / "data" / "secret" / "group1" / "0.in")
    os.symlink("../0.ans", symlinked / "data" / "secret" / "group1" / "0.ans")
    assert size_messages(symlinked) == []
    (symlinked / "data" / "secret" / "group2").mkdir()
    (symlinked / "data" / "secret" / "group2" / "0.in").write_bytes(b"c" * MIB)
    (symlinked / "data" / "secret" / "group2" / "0.ans").write_bytes(b"1\n")
    assert len(size_messages(symlinked)) == 1

    # .in without .ans is not a test case
    orphan = tmp_path / "orphan"
    make_problem(orphan, [b"a" * (MIB // 2)])
    (orphan / "data" / "secret" / "extra.in").write_bytes(b"b" * MIB)
    assert size_messages(orphan) == []

    # Broken symlinks are ignored
    broken = tmp_path / "broken"
    make_problem(broken, [b"a"])
    os.symlink("missing.ans", broken / "data" / "secret" / "0.ans.tmp")
    os.replace(broken / "data" / "secret" / "0.ans.tmp", broken / "data" / "secret" / "0.ans")
    assert size_messages(broken) == []
