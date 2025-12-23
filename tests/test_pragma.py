from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_pragma as check_pragma
from kattistools.args import get_argparser, argparse_to_args

def test_pragma_checker():
    errors = []
    def collect_error(path, e):
        nonlocal errors
        for _, value in e.items():
            errors += value
    problem_path = Path(__file__).parent / 'problems' / 'pragma'
    parser = get_argparser()
    args = parser.parse_args([str(problem_path), "--strict"])
    directory_dfs(argparse_to_args(args), [check_pragma.CheckPragma], [], collect_error)
    errors = ''.join(errors)
    BAD_FILES = ['unmitigated.cpp', 'optimization.cpp', 'multistring_target.cpp',
                 'splitpragma.cpp']
    BAD_FILES = [f'wrong_answer/{file}' for file in BAD_FILES]

    GOOD_FILES = ['manypragma.cpp', 'mitigate_pragma_allocator.cpp', 'accepted/ok2.cpp', 'wrong_answer/ok.cpp']
    GOOD_FILES = [f'accepted/{file}' for file in GOOD_FILES]

    for BAD_FILE in BAD_FILES:
        assert BAD_FILE in errors, f'Did not give error for file {BAD_FILE}'
    for GOOD_FILE in GOOD_FILES:
        assert GOOD_FILE not in errors, f'Gave unwarranted error for file {GOOD_FILE}'
