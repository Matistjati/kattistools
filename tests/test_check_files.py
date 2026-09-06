from pathlib import Path
import subprocess
from kattistools.checkers.check_files import CheckFiles
from kattistools.check_problem import run_checkers
from kattistools.args import Args

def test_check_files_binary():
    path = Path("tests/problems/binary_check")
    args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    
    all_messages = []
    def collect_error(p, e):
        nonlocal all_messages
        for msgs in e.values():
            all_messages.extend(msgs)

    run_checkers(args, [CheckFiles], [], [], collect_error)
    print(f"DEBUG: messages = {all_messages}")

    # Check that binary_file is flagged
    assert any("binary_file" in msg for msg in all_messages)

    # Check that script.sh is NOT flagged as binary
    assert not any("script.sh" in msg for msg in all_messages)

    # Check that text_file is NOT flagged
    assert not any("text_file" in msg for msg in all_messages)

    # Check that .git/git_binary is NOT flagged
    assert not any("git_binary" in msg for msg in all_messages)


def _disallowed_messages(path: Path):
    args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    all_messages = []
    def collect_error(p, e):
        for msgs in e.values():
            all_messages.extend(msgs)
    run_checkers(args, [CheckFiles], [], [], collect_error)
    return [m for m in all_messages if "Stray temporary file" in m or "Likely temporary folder" in m]


def _make_disallowed_problem(path: Path):
    path.mkdir()
    (path / "problem.yaml").write_text("name: x\n")
    (path / "score.txt").write_text("100\n")
    (path / "data_generation").mkdir()
    (path / "data").mkdir()
    (path / "data" / "perf.data").write_text("x\n")
    (path / "data" / "gen.old").write_text("x\n")
    # score.txt is only disallowed in the problem root
    (path / "data" / "score.txt").write_text("x\n")
    # .vscode is a repo-level concern (CheckRepoFiles), not CheckFiles'
    (path / ".vscode").mkdir()


def test_check_files_disallowed_without_git(tmp_path):
    problem = tmp_path / "problem"
    _make_disallowed_problem(problem)
    messages = _disallowed_messages(problem)

    assert any("'score.txt'" in m for m in messages)
    assert any("'data_generation'" in m for m in messages)
    assert any("data/perf.data" in m for m in messages)
    assert any("data/gen.old" in m for m in messages)
    assert not any("data/score.txt" in m for m in messages)
    assert not any(".vscode" in m for m in messages)


def test_check_files_disallowed_respects_gitignore(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    problem = tmp_path / "problem"
    _make_disallowed_problem(problem)
    (tmp_path / ".gitignore").write_text("*.data\n")
    (problem / ".gitignore").write_text("score.txt\n")
    messages = _disallowed_messages(problem)

    # Ignored by git: not reported
    assert not any("'score.txt'" in m for m in messages)
    assert not any("data/perf.data" in m for m in messages)
    # Not ignored: still reported
    assert any("'data_generation'" in m for m in messages)
    assert any("data/gen.old" in m for m in messages)


def test_check_files_disallowed_tracked_file_reported(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    problem = tmp_path / "problem"
    _make_disallowed_problem(problem)
    (tmp_path / ".gitignore").write_text("score.txt\n")
    # A tracked file gets pushed even if it matches .gitignore
    subprocess.run(["git", "-C", str(tmp_path), "add", "-f", "problem/score.txt"], check=True)
    messages = _disallowed_messages(problem)

    assert any("'score.txt'" in m for m in messages)
