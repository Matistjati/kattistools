from pathlib import Path
import yaml

from kattistools.checkers.checker import Checker

# Checks that IOI scoring will work on the problem
class IOIScoringChecker(Checker):
    def __init__(self, path):
        super().__init__("IOI scoring", path)
        self.handle_problem(path)

    def directory_is_custom_grader(self, path: Path, parent_value: bool) -> bool:
        if not (path / 'testdata.yaml').exists():
            return parent_value
        with open(path / 'testdata.yaml') as f:
            data = yaml.safe_load(f)
            if data and 'grading' in data:
                return 'custom' in data['grading']
            return parent_value

    def handle_problem(self, path):
        data = path / 'data'
        if not data.exists():
            return
        secret = data / 'secret'
        if not secret.exists():
            return

        data_custom = self.directory_is_custom_grader(data, False)
        secret_custom = self.directory_is_custom_grader(secret, data_custom)
        if data_custom or secret_custom:
            self.print_error("IOI scoring will not apply to this problem. Read mor here: https://github.com/Matistjati/Multiplicative_accept_score_Kattis")
