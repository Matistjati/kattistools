from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_consistent_source as check_consistent_source
from kattistools.args import parse_only_path_args

def test_consistent_source_checker():
    errors = []
    def collect_error(path, e):
        nonlocal errors
        for _, value in e.items():
            errors += value
    good_contest_path = Path(__file__).parent / 'problems' / 'sample_contest_ok_source'
    directory_dfs(parse_only_path_args(good_contest_path), [], [check_consistent_source.ConsistentSourceChecker], collect_error)
    assert not any(check_consistent_source.CONSISTENT_SOURCE_CHECKER_NAME in error for error in errors), "Gave false positive for mixing sources"

    errors = []
    bad_contest_path = Path(__file__).parent / 'problems' / 'sample_contest_bad_source'
    directory_dfs(parse_only_path_args(bad_contest_path), [], [check_consistent_source.ConsistentSourceChecker], collect_error)
    assert any(check_consistent_source.CONSISTENT_SOURCE_CHECKER_NAME in error for error in errors), "Did not give error when mixing sources"
