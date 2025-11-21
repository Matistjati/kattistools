from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_statement as check_statement
import kattistools.checkers.check_statement_files as check_statement_files

def test_yaml_checker():
    errors = []
    def collect_error(path, e):
        nonlocal errors
        for _, value in e.items():
            errors += value
    problem_path = Path(__file__).parent / 'problems' / 'tikz'
    directory_dfs(problem_path, [check_statement.CheckStatement, check_statement_files.CheckStatementFiles], [], collect_error)
    assert len(errors) == 0, f'Errors found: {errors}'
    bad_problems = ['problem_tex', 'probelm', 'problem_eng', 'problem_copy']
    for bad_problem in bad_problems:
        problem_path = Path(__file__).parent / 'problems' / bad_problem
        errors = []
        directory_dfs(problem_path, [check_statement.CheckStatement, check_statement_files.CheckStatementFiles], [], collect_error)
        error_str = ''.join(errors).lower()
        #print(f"problem: {bad_problem}", error_str, "\n")
        assert not 'no statement' in error_str, f'Failed to find statement in bad problem {bad_problem}'
        assert len(errors) > 0, f'No errors found in bad problem {bad_problem}'
