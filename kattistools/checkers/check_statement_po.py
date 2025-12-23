from pathlib import Path
import re

from kattistools.common import edit_distance
from kattistools.checkers.checker import Checker
from kattistools.args import Args
from kattistools.checkers.check_subtask_box import parse_subtask_box

def any_has(lines, needle):
    return any(needle in line for line in lines)

def any_begins(lines, needle):
    return any(line.startswith(needle) for line in lines)

def read_file(path):
    with open(path, "r") as f:
        return f.readlines()


class CheckStatementPO(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("PO statement", path, args)
        self.handle_problem(path)


    def handle_swedish(self, path):
        lines = set(read_file(path))
        if not self.is_interactive_problem() and not any_begins(lines, r"\section*{Indata}"):
            self.print_error(r"(sv) missing \section*{Indata}")
        if not self.is_interactive_problem() and not any_begins(lines, r"\section*{Utdata}"):
            self.print_error(r"(sv) missing \section*{Utdata}")

        if not any_begins(lines, "Din lösning kommer att testas på en mängd testfallsgrupper."):
            self.print_warning("(sv) Missing poängsättning-section")

        box = parse_subtask_box(path)

        if box:
            LAST_SUBTASK_TEXT = "Inga ytterligare begränsningar."
            for line in box.subtask_lines:
                constraints = line.constraints.strip()
                if 1 <= edit_distance(LAST_SUBTASK_TEXT, constraints) < 4:
                    self.print_warning(f"(sv) Likely typo: you wrote \"{constraints}\" in subtask box, you want \"{LAST_SUBTASK_TEXT}\"")


    def handle_english(self, path):
        lines = set(read_file(path))
        if not self.is_interactive_problem() and not any_begins(lines, r"\section*{Input}"):
            self.print_error(r"(en) missing \section*{Input}")
        if not self.is_interactive_problem() and not any_begins(lines, r"\section*{Output}"):
            self.print_error(r"(en) missing \section*{Output}")
        
        if not any_begins(lines, r"\section*{Scoring}"):
            self.print_warning(r"(en) Missing \section*{Scoring}")

        if not any_begins(lines, "Your solution will be tested on a set of test groups, each worth a number of points. Each test group contains"):
            self.print_warning("(en) Missing scoring text")            
        
        box = parse_subtask_box(path)

        if box:
            LAST_SUBTASK_TEXT = "No additional constraints."
            for line in box.subtask_lines:
                constraints = line.constraints.strip()
                if 1 <= edit_distance(LAST_SUBTASK_TEXT, constraints) < 4:
                    self.print_warning(f"(en) Likely typo: you wrote \"{constraints}\" in subtask box, you want \"{LAST_SUBTASK_TEXT}\"")

    def handle_problem(self, path):
        self.add_message_condition(self.is_po_problem)
        statement_path = path / 'problem_statement'
        if not statement_path.exists():
            return

        statements = statement_path.glob('*.tex')
        for statement in statements:
            if ".sv" in statement.name:
                self.handle_swedish(statement)
            if ".en" in statement.name:
                self.handle_english(statement)
