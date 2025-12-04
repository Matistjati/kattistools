from pathlib import Path
import yaml

from kattistools.checkers.checker import Checker
from kattistools.common import is_problem, edit_distance


class UniqueUUIDChecker(Checker):
    def __init__(self, path):
        super().__init__("Unique UUID:s", path)
        self.handle_contest(path)

    def gather_problems(self, path: Path):
        problems = []
        for item in path.glob('*'):
            if is_problem(item):
                problems.append(item)
        return problems

    def handle_contest(self, path):
        problems = self.gather_problems(path)
        uuids = {}
        for problem in problems:
            with open(problem / 'problem.yaml', 'r') as f:
                problem_yaml = yaml.safe_load(f) or {}
                if 'uuid' in problem_yaml:
                    uuid = problem_yaml['uuid']
                    if uuid in uuids:
                        self.print_error(f"UUID collision: both {problem} and {uuids[uuid]} have same UUID")
                    else:
                        uuids[uuid] = problem
        
        