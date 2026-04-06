from pathlib import Path
import sys
import re

from rich.console import Console

BLUE="#52b2f7"

from kattistools.checkers.checker import Checker
from kattistools.checkers.check_generator import GeneratorChecker
from kattistools.checkers.check_yaml import ProblemYamlChecker
from kattistools.checkers.check_subtask_score import CheckScoreMatchesStatement
from kattistools.checkers.check_template import CheckCPPTemplate
from kattistools.checkers.check_statement import CheckStatement
from kattistools.checkers.check_statement_files import CheckStatementFiles
from kattistools.checkers.check_statement_po import CheckStatementPO
from kattistools.checkers.check_subtask_box import CheckSubtaskBox
from kattistools.checkers.check_files import CheckFiles
from kattistools.checkers.check_has_languages import CheckStatementLanguages
from kattistools.checkers.check_pragma import CheckPragma
from kattistools.checkers.check_ioi_scoring import IOIScoringChecker
from kattistools.checkers.check_input_validator import CheckInputValidator
from kattistools.checkers.check_data_yaml import CheckDataYAML
from kattistools.checkers.check_consistent_source import ConsistentSourceChecker
from kattistools.checkers.check_unique_uuid import UniqueUUIDChecker
from kattistools.checkers.check_testdata_tools import TestdataToolsChecker
from kattistools.common import *
from kattistools.args import Args, parse_cmdline_args

# Run once per problem
per_problem_checkers = [
    CheckFiles,
    GeneratorChecker,
    ProblemYamlChecker,
    CheckScoreMatchesStatement,
    CheckStatement,
    CheckStatementPO,
    CheckSubtaskBox,
    CheckStatementLanguages,
    CheckPragma,
    CheckStatementFiles,
    IOIScoringChecker,
    CheckCPPTemplate,
    CheckInputValidator,
    CheckDataYAML
]

# The parent directory of a problem is a contest, and these checkers are run once per contest
contest_checkers = [
    ConsistentSourceChecker,
    UniqueUUIDChecker
]

# From every problem, traverse upwards until we find a folder with .git. Run these checkers here
repo_checkers = [
    UniqueUUIDChecker,
    TestdataToolsChecker
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

def directory_dfs(args: Args, per_problem_checkers, contest_checkers, error_callback, skip_callback=None):
    return run_checkers(args, per_problem_checkers, contest_checkers, error_callback, skip_callback)

def run_checkers(args: Args, per_problem_checkers, contest_checkers, error_callback, skip_callback=None):
    problems = gather_problems(args.path)

    def deduplicate(items):
        # Since python 3.7, dicts preserve insertion order
        return list(dict.fromkeys(items))
    assert problems == deduplicate(problems)
    contests = deduplicate(problem.parent for problem in problems)
    repos = []
    for problem in problems:
        path = problem.resolve()
        while path != path.parent:
            if (path / ".git").exists():
                repos.append(path)
                break
            path = path.parent
    repos = deduplicate(repos)

    seen = []
    def _run_checkers(checkers, dir):
        errors = {}
        for check in checkers:
            if (check, dir) in seen:
                continue
            seen.append((check, dir))

            checker = check(dir, args)
            for error_name, error_list in checker.errors.items():
                error_list = [f"{i} ({checker.name})" for i in error_list]
                if error_name not in errors:
                    errors[error_name] = []
                errors[error_name] += error_list
            if checker.skips and skip_callback:
                skip_callback(dir, checker.skips)

        if errors:
            error_callback(dir, errors)
    
    for problem in problems:
        _run_checkers(per_problem_checkers, problem)
    for contest in contests:
        _run_checkers(contest_checkers, contest)
    for repo in repos:
        _run_checkers(repo_checkers, repo)

if __name__ == "__main__":
    args = parse_cmdline_args()
    
    directory = args.path
    if not Path(directory).exists():
        console.print(f"[red]Error[/red]: folder {directory} does not exist")
        sys.exit(1)



    run_checkers(args, per_problem_checkers, contest_checkers, print_errors, aggregate_skips)

    if all_skips:
        console.print(f"[{BLUE}]Info[/{BLUE}]: suppressed errors/warnings because following modes were not set")
        for skip_reason, amount in all_skips.items():
            console.print(f"\t{skip_reason}: {amount}")
