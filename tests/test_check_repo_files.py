from pathlib import Path
import subprocess
from kattistools.checkers.check_repo_files import CheckRepoFiles
from kattistools.check_problem import run_checkers
from kattistools.args import Args


def _make_repo(root: Path, gitignore: str | None):
    """root/.vscode, root/score.txt, root/contest1/.vscode, root/contest1/problem1/.vscode"""
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    if gitignore is not None:
        (root / ".gitignore").write_text(gitignore)
    (root / ".vscode").mkdir()
    (root / "score.txt").write_text("100\n")
    problem = root / "contest1" / "problem1"
    problem.mkdir(parents=True)
    (problem / "problem.yaml").write_text("name: x\n")
    (root / "contest1" / ".vscode").mkdir()
    (problem / ".vscode").mkdir()
    # Never reported: lives under an excluded directory
    (root / ".git" / ".vscode").mkdir()
    (root / "testdata_tools" / ".vscode").mkdir(parents=True)
    return problem


def _repo_messages(problem: Path):
    args = Args(path=problem, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    messages = {}
    def collect(p, e):
        messages[p] = [m for msgs in e.values() for m in msgs]
    run_checkers(args, [], [], [CheckRepoFiles], collect)
    return messages


def test_repo_files_reports_vscode_anywhere(tmp_path):
    problem = _make_repo(tmp_path, gitignore="")
    messages = _repo_messages(problem)

    # Reported once, against the repo root, not against the problem
    assert list(messages) == [tmp_path.resolve()]
    msgs = messages[tmp_path.resolve()]
    assert any("'.vscode'" in m for m in msgs)
    assert any("'contest1/.vscode'" in m for m in msgs)
    assert any("'contest1/problem1/.vscode'" in m for m in msgs)
    assert any("'score.txt'" in m for m in msgs)
    assert not any(".git/" in m or "testdata_tools" in m for m in msgs)


def test_repo_files_respects_gitignore(tmp_path):
    problem = _make_repo(tmp_path, gitignore=".vscode/\n")
    msgs = _repo_messages(problem)[tmp_path.resolve()]

    assert not any(".vscode" in m for m in msgs)
    assert any("'score.txt'" in m for m in msgs)

