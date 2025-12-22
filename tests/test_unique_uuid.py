from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_unique_uuid as check_unique_uuid
from kattistools.args import parse_only_path_args

def test_consistent_source_checker():
    errors = []
    def collect_error(path, e):
        nonlocal errors
        for _, value in e.items():
            errors += value
    bad_contest_path = Path(__file__).parent / 'problems' / 'contest_uuid_collision'
    directory_dfs(parse_only_path_args(bad_contest_path), [], [check_unique_uuid.UniqueUUIDChecker], collect_error)
    assert any("UUID collision" in error for error in errors), "Did not give error on UUID collision"
