from pathlib import Path

from kattistools.common import get_statements
from kattistools.checkers.checker import Checker
import re

class CheckFiles(Checker):
    def __init__(self, path):
        super().__init__("Problem files", path)
        self.handle_problem(path)

    def check_input_validator(self, path):
        if not (path / 'input_validators').exists():
            if (path / 'input_format_validators').exists():
                self.print_error("input_format_validators is renamed to input_validators")
            else:
                self.print_error('No input validator')

    def check_testdata_root(self, path):
        if (path / "testdata.yaml").exists():
            self.print_error("testdata.yaml in root")

    def handle_problem(self, path):
        self.check_input_validator(path)
        self.check_testdata_root(path)
