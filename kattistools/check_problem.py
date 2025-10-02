import os
import subprocess
from pathlib import Path
import argparse
import sys

from rich.console import Console

EXCLUDED_DIRS = [".git", "testdata_tools"]
BLUE="#52b2f7"

from kattistools.checkers.check_generator import GeneratorChecker
from kattistools.checkers.check_yaml import ProblemYamlChecker
from kattistools.checkers.check_subtask_score import CheckScoreMatchesStatement
from kattistools.checkers.check_shebang import CheckPythonShebang
from kattistools.checkers.check_statement import CheckStatement
from kattistools.checkers.check_files import CheckFiles
from kattistools.checkers.check_has_languages import CheckStatementLanguages
from kattistools.checkers.check_pragma import CheckPragma
from kattistools.checkers.check_consistent_source import ConsistentSourceChecker
from kattistools.common import *

checkers = [
    GeneratorChecker,
    ProblemYamlChecker,
    CheckScoreMatchesStatement,
    CheckPythonShebang,
    CheckStatement,
    CheckFiles,
    CheckStatementLanguages,
    CheckPragma
]

contest_checkers = [
    ConsistentSourceChecker
]

def is_interactive(path: Path):
    if not (path / 'problem.yaml').exists():
        return False
    with open(path / "problem.yaml", "r") as f:
        return "interactive" in f.read()


console = Console()
def print_errors(path: Path, errors):
    special = []
    if is_interactive(path):
        special.append("interactive")
    if (path / "graders").exists():
        special.append("grader")
    if (path / "include").exists():
        special.append("include")
    interactive_msg = f" ({', '.join(special)})" if special else ""
    console.print(f"> {path.parent.name}/[{BLUE}]{path.name}[/{BLUE}]{interactive_msg}:")
    for error, error_list in reversed(sorted(errors.items())):
        console.print(error)
        console.print("\n".join(error_list))
    console.print("--------------\n\n")


# Each checker is involved in the root of each problem exactly once
def directory_dfs(path: Path, problem_checkers, contest_checkers, error_callback):
    if any(path.name.endswith(exclude) for exclude in EXCLUDED_DIRS):
        return
    
    if path.is_file():
        return
    
    def run_checkers(checkers):
        errors = {}
        for check in checkers:
            checker = check(path)
            for error_name, error_list in checker.errors.items():
                error_list = [f"{i} ({checker.name})" for i in error_list]
                if error_name not in errors:
                    errors[error_name] = []
                errors[error_name] += error_list
            
        if errors:
            error_callback(path, errors)

    if is_problem(path):
        run_checkers(problem_checkers)
        return
    else:
        run_checkers(contest_checkers)

    children = path.iterdir()
    for dir in reversed(sorted(children)):
        directory_dfs(dir, problem_checkers, contest_checkers, error_callback)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stylecheck PO problems')
    parser.add_argument('directory', help='Directory to recursively stylecheck')
    args = parser.parse_args()
    
    directory = args.directory
    if not Path(directory).exists():
        console.print(f"[red]Error[/red]: folder {directory} does not exist")
        sys.exit(0)
    directory_dfs(Path(directory), checkers, contest_checkers, print_errors)
    