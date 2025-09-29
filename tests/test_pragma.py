from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_pragma as check_pragma

def test_pdf_render_verifyproblem():
    errors = []
    def collect_error(path, e):
        nonlocal errors
        for _, value in e.items():
            errors += value
    problem_path = Path(__file__).parent / 'problems' / 'pragma'
    directory_dfs(problem_path, [check_pragma.CheckPragma], collect_error)
    errors = ''.join(errors)
    BAD_FILES = ['accepted/bad1.cpp', 'accepted/bad2.cpp', 'wrong_answer/bad.cpp']
    GOOD_FILES = ['accepted/ok1.cpp', 'accepted/ok2.cpp', 'wrong_answer/ok.cpp']

    for BAD_FILE in BAD_FILES:
        assert BAD_FILE in errors, f'Did not give error for file {BAD_FILE}'
    for GOOD_FILE in GOOD_FILES:
        assert GOOD_FILE not in errors, f'Gave unwarranted error for file {GOOD_FILE}'
