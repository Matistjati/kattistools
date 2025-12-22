from pathlib import Path

from kattistools.common import get_statements
from kattistools.checkers.checker import Checker
from kattistools.args import Args

class CheckFiles(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Problem files", path, args)
        self.handle_problem(path)

    def check_input_validator(self, path):
        if not (path / 'input_validators').exists():
            if (path / 'input_format_validators').exists():
                self.print_error("input_format_validators is renamed to input_validators")
            else:
                self.print_error('Problem has no input validator')

    def check_testdata_root(self, path):
        if (path / "testdata.yaml").exists():
            self.print_error("testdata.yaml in root")

    def check_statements(self, path):
        statement_path = path / "problem_statement"
        if not (statement_path).exists():
            self.print_error("Problem has no problem statement")
            return

        if self.is_po_problem() and not (statement_path / "problem.sv.tex").exists():
            self.print_warning("problem.sv.tex is missing")

        if not (statement_path / "problem.en.tex").exists():
            self.print_warning("problem.en.tex is missing")

    def check_testdata(self, path):
        data_path = path / 'data'
        if not data_path.exists():
            self.print_error("Problem has no test data")

        if not (data_path / 'secret'):
            self.print_warning("Problem has no secret test data")

        if not (data_path / 'sample'):
            self.print_warning("Problem has no sample test data")


    def handle_problem(self, path):
        self.check_input_validator(path)
        self.check_testdata_root(path)
        self.check_statements(path)
        self.check_testdata(path)
