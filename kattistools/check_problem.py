from pathlib import Path
import argparse
import sys
import re

from rich.console import Console

EXCLUDED_DIRS = [".git", "testdata_tools"]
BLUE="#52b2f7"

from kattistools.checkers.checker import Checker
from kattistools.checkers.check_generator import GeneratorChecker
from kattistools.checkers.check_yaml import ProblemYamlChecker
from kattistools.checkers.check_subtask_score import CheckScoreMatchesStatement
from kattistools.checkers.check_shebang import CheckPythonShebang
from kattistools.checkers.check_template import CheckCPPTemplate
from kattistools.checkers.check_statement import CheckStatement
from kattistools.checkers.check_statement_files import CheckStatementFiles
from kattistools.checkers.check_statement_po import CheckStatementPO
from kattistools.checkers.check_subtask_box import CheckSubtaskBox
from kattistools.checkers.check_files import CheckFiles
from kattistools.checkers.check_has_languages import CheckStatementLanguages
from kattistools.checkers.check_pragma import CheckPragma
from kattistools.checkers.check_ioi_scoring import IOIScoringChecker
from kattistools.checkers.check_consistent_source import ConsistentSourceChecker
from kattistools.checkers.check_unique_uuid import UniqueUUIDChecker
from kattistools.common import *
from kattistools.args import Args, parse_cmdline_args

default_checkers = [
    GeneratorChecker,
    ProblemYamlChecker,
    CheckScoreMatchesStatement,
    CheckPythonShebang,
    CheckStatement,
    CheckStatementPO,
    CheckSubtaskBox,
    CheckFiles,
    CheckStatementLanguages,
    CheckPragma,
    CheckStatementFiles,
    IOIScoringChecker,
    CheckCPPTemplate,
]

contest_checkers = [
    ConsistentSourceChecker,
    UniqueUUIDChecker
]

def find_rightmost_year(path: Path) -> int | None:
    year_pattern = re.compile(r'\b(19[7-9]\d|20\d\d|2100)\b')
    
    for part in reversed(path.parts):
        match = year_pattern.search(part)
        if match:
            return int(match.group(0))
    return None

console = Console()
def print_errors(path: Path, errors):
    special = []
    year = find_rightmost_year(path)
    if is_interactive(path):
        special.append("interactive")
    if (path / "graders").exists():
        special.append("grader")
    if (path / "include").exists():
        special.append("include")
    interactive_msg = f" ({', '.join(special)})" if special else ""
    year_msg = f" ({year})" if year else ''
    console.print(f"> {path.parent.name}/[{BLUE}]{path.name}[/{BLUE}]{year_msg}{interactive_msg}:")
    for error, error_list in reversed(sorted(errors.items())):
        console.print(error)
        console.print("\n".join(error_list))
    console.print("--------------\n\n")

all_skips = {}
def aggregate_skips(path: Path, skips):
    for skip_reason, amount in skips.items():
        if skip_reason not in all_skips:
            all_skips[skip_reason] = 0
        all_skips[skip_reason] += amount

# Each checker is involved in the root of each problem exactly once
def directory_dfs(args: Args, problem_checkers, contest_checkers, error_callback, skip_callback=None):
    def _directory_dfs(path: Path):
        if any(path.name.endswith(exclude) for exclude in EXCLUDED_DIRS):
            return

        if path.is_file():
            return

        def run_checkers(checkers):
            errors = {}
            for check in checkers:
                checker = check(path, args)
                for error_name, error_list in checker.errors.items():
                    error_list = [f"{i} ({checker.name})" for i in error_list]
                    if error_name not in errors:
                        errors[error_name] = []
                    errors[error_name] += error_list
                if checker.skips and skip_callback:
                    skip_callback(path, checker.skips)

            if errors:
                error_callback(path, errors)
            
        if is_problem(path):
            run_checkers(problem_checkers)
            return
        else:
            run_checkers(contest_checkers)

        children = path.iterdir()
        for dir in reversed(sorted(children)):
            _directory_dfs(dir)

    _directory_dfs(args.path)

if __name__ == "__main__":
    args = parse_cmdline_args()
    
    directory = args.path
    if not Path(directory).exists():
        console.print(f"[red]Error[/red]: folder {directory} does not exist")
        sys.exit(1)

    directory_dfs(args, default_checkers, contest_checkers, print_errors, aggregate_skips)

    if all_skips:
        console.print(f"[{BLUE}]Info[/{BLUE}]: suppressed errors/warnings because following modes were not set")
        for skip_reason, amount in all_skips.items():
            console.print(f"\t{skip_reason}: {amount}")
