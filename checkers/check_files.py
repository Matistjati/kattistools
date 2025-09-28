import os
from pathlib import Path

from kattistools.common import *
from kattistools.checkers.checker import Checker
import re

class CheckFiles(Checker):
    def __init__(self, path):
        super().__init__("Statement files", path)
        self.handle_problem(path)

    def check_statement_files(self, path: Path):
        if not (path / 'problem_statement').exists():
            self.print_error("no statement")
            return
        
        statement_path = path / "problem_statement"

        for statement in list(statement_path.rglob("*.tex")) + list(statement_path.rglob("*.md")):
            name = statement.name
            if name.count(".")==1:
                self.print_error(f"Statement name {name} lacks language code (e.g .sv)")
            pattern = r'^(problem\..+\.(tex|md))$'
            if not re.fullmatch(pattern, name):
                self.print_error(f"Statement name {name} does not match problem.<language>.md or problem.<language>.tex")

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
        path=Path(path)
        self.check_statement_files(path)
        self.check_input_validator(path)
        self.check_testdata_root(path)
