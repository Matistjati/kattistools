import os
import subprocess
from pathlib import Path
import argparse
import sys

from rich.console import Console

# Add parent directory to path so my LSP will be happy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

EXCLUDED_DIRS = [".git", "testdata_tools"]
BLUE="#52b2f7"

from checkers.check_generator import GeneratorChecker
from checkers.check_yaml import ProblemYamlChecker
from checkers.check_subtask_score import CheckScoreMatchesStatement
from checkers.check_shebang import CheckPythonShebang
from checkers.check_statement import CheckStatement
from checkers.check_files import CheckFiles
from checkers.check_has_languages import CheckStatementLanguages
from checkers.check_pragma import CheckPragma
from kattistools.common import *

checkers = [GeneratorChecker,
            ProblemYamlChecker,
            CheckScoreMatchesStatement,
            CheckPythonShebang,
            CheckStatement,
            CheckFiles,
            CheckStatementLanguages,
            CheckPragma
            ]

def is_interactive(path: Path):
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

def is_problem(path: Path):
    return (path / 'problem.yaml').exists()

# Each checker is involved in the root of each problem exactly once
def directory_dfs(path: Path):
    if any(path.name.endswith(exclude) for exclude in EXCLUDED_DIRS):
        return
    
    if path.is_file():
        return

    if is_problem(path):
        errors = {}
        for check in checkers:
            checker = check(str(path))
            for error_name, error_list in checker.errors.items():
                error_list = [f"{i} ({checker.name})" for i in error_list]
                if error_name not in errors:
                    errors[error_name] = []
                errors[error_name] += error_list
            
        if errors:
            print_errors(path, errors)
        return

    children = path.iterdir()
    for dir in reversed(sorted(children)):
        directory_dfs(dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stylecheck PO problems')
    parser.add_argument('directory', help='Directory to recursively stylecheck')
    args = parser.parse_args()
    
    directory = args.directory
    if not Path(directory).exists():
        console.print(f"[red]Error[/red]: folder {directory} does not exist")
        sys.exit(0)
    directory_dfs(Path(directory))
    