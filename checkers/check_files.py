import os
from pathlib import Path

from kattistools.common import *
from kattistools.checkers.checker import Checker
import re



class CheckFiles(Checker):
    def __init__(self, path):
        super().__init__("Statement files", path)
        self.handle_problem(path)

    def check_statement_files(self, path):
        if not folder_exists(path, "problem_statement"):
            self.print_error("no statement")
            return
        
        statement_path = Path(path) / "problem_statement"

        statements = [file for file in get_files(statement_path) if file.endswith(".tex") or file.endswith(".md")]
        for statement in statements:
            name = os.path.basename(statement)
            if name.count(".")==1:
                self.print_error(f"Statement name {name} lacks language code (e.g .sv)")
            pattern = r'^(problem\..+\.(tex|md))$'
            if not re.fullmatch(pattern, name):
                self.print_error(f"Statement name {name} does not match problem.<language>.md or problem.<language>.tex")

    def check_input_validator(self, path):
        if not folder_exists(path, "input_validators"):
            if folder_exists(path, "input_format_validators"):
                self.print_error("input_format_validators is renamed to input_validators")
            else:
                self.print_error("No input validator")

    def check_testdata_root(self, path):
        if (Path(path) / "testdata.yaml").exists():
            self.print_error("testdata.yaml in root")

    def handle_problem(self, path):
        self.check_statement_files(path)
        self.check_input_validator(path)
        self.check_testdata_root(path)

