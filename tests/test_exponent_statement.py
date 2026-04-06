from pathlib import Path

from kattistools.check_problem import run_checkers
import kattistools.checkers.check_statement as check_statement
from kattistools.args import path_to_args

def test_pragma_checker():
    errors = []
    def collect_error(path, e):
        nonlocal errors
        for _, value in e.items():
            errors += value
    problem_path = Path(__file__).parent / 'problems' / 'latex_exponents'
    run_checkers(path_to_args(problem_path), [check_statement.CheckStatement], [], collect_error)
    errors = ''.join(errors)
    BAD_FILES = ['en', 'sv']
    BAD_FILES = [f'({language}) statement: you probably forgot to add brackets' for language in BAD_FILES]

    GOOD_FILES = ['da', 'ja']
    GOOD_FILES = [f'({language}) statement: you probably forgot to add brackets' for language in GOOD_FILES]

    for BAD_FILE in BAD_FILES:
        assert BAD_FILE in errors, f'Did not give error for file {BAD_FILE}'
    for GOOD_FILE in GOOD_FILES:
        assert GOOD_FILE not in errors, f'Gave unwarranted error for file {GOOD_FILE}'
