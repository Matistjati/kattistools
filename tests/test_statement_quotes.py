from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_statement as check_statement
from kattistools.args import parse_only_path_args

def test_pragma_checker():
    errors = {}
    def collect_error(path, e):
        nonlocal errors
        assert not any("good" in part for part in path.parts)
        if path not in errors:
            errors[path] = []
        for _, value in e.items():
            errors[path] += value
    problem_path = Path(__file__).parent / 'problems' / 'quotes'
    directory_dfs(parse_only_path_args(problem_path), [check_statement.CheckStatement], [], collect_error)
    
    num_quote_errors = sum(1 if any("Don't use" in err for err in errs) else 0 for errs in errors.values())
    assert num_quote_errors == len(list(problem_path.glob("*_bad*")))
