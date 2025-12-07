from pathlib import Path

from kattistools.common import edit_distance
from kattistools.checkers.checker import Checker

class CheckStatementLanguages(Checker):
    def __init__(self, path):
        super().__init__("statement language", path)
        self.is_interactive = False
        self.handle_problem(path)

    def handle_problem(self, path):
        if not (path / 'problem_statement').exists():
            return

        statement_path = Path(path) / "problem_statement"

        known = ["problem.sv.tex", "problem.en.tex", "problem.da.tex"]
        for file in statement_path.glob("*"):
            if file.name not in known:
                closest_dist = 100000
                closest_name = ""

                for name in known:
                    d = edit_distance(file.name, name)
                    if d < closest_dist:
                        closest_dist = d
                        closest_name = name
                
                if closest_dist<=3:
                    self.print_error(f"Did you misspell {file.name}? Similar to {closest_name}")

