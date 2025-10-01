from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_yaml as check_yaml

def test_yaml_checker():
    errors = []
    def collect_error(path, e):
        nonlocal errors
        for _, value in e.items():
            errors += value
    #good_contest_path = Path(__file__).parent / 'problems' / 'sample_contest_ok'
    #directory_dfs(good_contest_path, [check_yaml.ProblemYamlChecker], [], collect_error)
    ...
