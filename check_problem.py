import os
import subprocess
import argparse
import sys

# Add the parent directory of 'kattistools' to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from checkers.check_subtask_order import SubtaskOrderChecker
from checkers.check_yaml import ProblemYamlChecker
from checkers.check_subtask_score import CheckScoreMatchesStatement
from checkers.check_shebang import CheckPythonShebang
from checkers.check_statement import CheckStatement
from kattistools.common import *

checkers = [SubtaskOrderChecker,
            ProblemYamlChecker,
            CheckScoreMatchesStatement,
            CheckPythonShebang,
            CheckStatement
            ]

def is_problem(path):
    return 

excluded_dirs = [".git", "testdata_tools"]

def directory_dfs(path):
    if any(path.endswith(exclude) for exclude in excluded_dirs):
        return

    is_problem = os.path.isfile(os.path.join(path, "problem.yaml"))
    if is_problem:
        for check in checkers:
            check(path)
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
    