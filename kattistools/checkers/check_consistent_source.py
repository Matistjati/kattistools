from pathlib import Path
import yaml

from kattistools.checkers.checker import Checker
from kattistools.common import is_problem, edit_distance

CONSISTENT_SOURCE_CHECKER_NAME = 'Consistent source'

# Checks that there are no typos in source
# Checks in a per-contest level, so we check all problems in the folder
# For example, if we find
# NCPC 2025
# and
# NPCC 2024
# in the same folder, that's a likely miss
class ConsistentSourceChecker(Checker):
    def __init__(self, path):
        super().__init__(CONSISTENT_SOURCE_CHECKER_NAME, path)
        self.handle_contest(path)

    def gather_problems(self, path: Path):
        problems = []
        for item in path.glob('*'):
            if is_problem(item):
                problems.append(item)
        return problems

    def handle_contest(self, path):
        problems = self.gather_problems(path)
        sources = []
        for problem in problems:
            with open(problem / 'problem.yaml', 'r') as f:
                problem_yaml = yaml.safe_load(f) or {}
                if 'source' in problem_yaml:
                    sources.append(problem_yaml['source'])
        
        similar_pairs = set()
        for source_1 in sources:
            for source_2 in sources:
                if source_1 == source_2:
                    continue
                distance = edit_distance(source_1, source_2)
                if distance <= 3:
                    similar_pairs.add((min(source_1, source_2), max(source_1, source_2)))
        for source_1, source_2 in similar_pairs:
            self.print_error(f"Problem sources {source_1} and {source_2} are similar but not same, typo?")
