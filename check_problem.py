import os
import subprocess
from pathlib import Path
import argparse
import sys

from rich.console import Console

# Add the parent directory of 'kattistools' to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from checkers.check_generator import GeneratorChecker
from checkers.check_yaml import ProblemYamlChecker
from checkers.check_subtask_score import CheckScoreMatchesStatement
from checkers.check_shebang import CheckPythonShebang
from checkers.check_statement import CheckStatement
from checkers.check_files import CheckFiles
from checkers.check_has_languages import CheckStatementLanguages
from kattistools.common import *

checkers = [GeneratorChecker,
            ProblemYamlChecker,
            CheckScoreMatchesStatement,
            CheckPythonShebang,
            CheckStatement,
            CheckFiles,
            CheckStatementLanguages
            ]

def is_interactive(path):
    with open(Path(path) / "problem.yaml", "r") as f:
        return "interactive" in f.read()

excluded_dirs = [".git", "testdata_tools"]

silentmode = False

console = Console()
def print_errors(path, errors):
    special = []
    if is_interactive(path):
        special.append("interactive")
    if (Path(path) / "graders").exists():
        special.append("grader")
    if (Path(path) / "include").exists():
        special.append("include")
    interactive_msg = f" ({', '.join(special)})" if special else ""
    console.print(f"> {Path(path).parent.name}/[#52b2f7]{get_node_name(path)}[/#52b2f7]{interactive_msg}:")
    for error, error_list in reversed(sorted(errors.items())):
        console.print(error)
        console.print("\n".join(error_list))
    console.print("--------------\n")

# Each checker is involved in the root of each problem exactly once
def directory_dfs(path, ignoredproblems):
    if any(path.endswith(exclude) for exclude in excluded_dirs):
        return

    is_problem = os.path.isfile(os.path.join(path, "problem.yaml"))

    if is_problem:
        if Path(path).name in ignoredproblems:
            if silentmode:
                return 
            console.print(f"Skipping [#52b2f7]{Path(path).name}[/#52b2f7] as it is in the ignore list.")
            console.print("--------------\n")
            return


        errors = {}
        for check in checkers:
            checker = check(path)
            for error_name, error_list in checker.errors.items():
                error_list = [f"{i} ({checker.name})" for i in error_list]
                if error_name not in errors:
                    errors[error_name] = []
                errors[error_name] += error_list
            
        if errors:
            print_errors(path, errors)
        return

    children = get_subdirectiories(path)
    for dir in reversed(sorted(children)):
        directory_dfs(dir, ignoredproblems)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stylecheck PO problems')
    parser.add_argument('directory', help='Directory to recursively stylecheck')
    parser.add_argument("-s", "-i", "--skip", "--ignore", metavar='PROBLEM ID', nargs="*", help='Problem IDs to ignore')
    parser.add_argument("--silent", action="store_true", help='Only print warnings and errors')

    args = parser.parse_args()

    ignoredproblems = set(args.skip) if args.skip else set()

    silentmode = args.silent

    directory = args.directory
    if not Path(directory).exists():
        console.print(f"[red]Error[/red]: folder {directory} does not exist")
        sys.exit(0)

    directory_dfs(directory, ignoredproblems)
    