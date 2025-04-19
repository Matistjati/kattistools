import os
import subprocess
import argparse
import sys

# Add the parent directory of 'kattistools' to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from checkers.check_generator import GeneratorChecker
from checkers.check_yaml import ProblemYamlChecker
from checkers.check_subtask_score import CheckScoreMatchesStatement
from checkers.check_shebang import CheckPythonShebang
from checkers.check_statement import CheckStatement
from checkers.check_statement_files import CheckStatementFiles
from kattistools.common import *

checkers = [GeneratorChecker,
            ProblemYamlChecker,
            CheckScoreMatchesStatement,
            CheckPythonShebang,
            CheckStatement,
            CheckStatementFiles
            ]

def is_problem(path):
    return 

excluded_dirs = [".git", "testdata_tools"]

# Each checker is involved in the root of each problem exactly once
def directory_dfs(path):
    if any(path.endswith(exclude) for exclude in excluded_dirs):
        return

    is_problem = os.path.isfile(os.path.join(path, "problem.yaml"))
    if is_problem:
        errors = {}
        for check in checkers:
            checker = check(path)
            for error_name, error_list in checker.errors.items():
                error_list = [f"{i} ({checker.name})" for i in error_list]
                if error_name not in errors:
                    errors[error_name] = []
                errors[error_name] += error_list
            
        if errors:
            print(f"\"{get_node_name(path)}\" potential errors ({os.path.normpath(path).split(os.path.sep)[-2]}):")
            for error, error_list in errors.items():
                print(error)
                print("\n".join(error_list))
            print("*****\n\n")
        return

    children = get_subdirectiories(path)
    for dir in children:
        directory_dfs(dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stylecheck PO problems')
    parser.add_argument('directory', help='Directory to recursively stylecheck')
    args = parser.parse_args()
    
    directory = args.directory
    directory_dfs(directory)
    