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

        if not any_begins(lines, r"\section*{Poängsättning}"):
            self.print_warning("Missing poängsättning-section")
        else:
            scoring_text = [
                r"\section*{Poängsättning}",
                r"Din lösning kommer att testas på en mängd testfallsgrupper.",
                r"För att få poäng för en grupp så måste du klara alla testfall i gruppen."
            ]
            has_scoring_text = False
            with open(path, "r") as f:
                statement = [line.replace("\n", "") for line in f.readlines()]
                has_scoring_text = any(
                    statement[i] == scoring_text[0] and
                    statement[i+1] == scoring_text[1] and
                    statement[i+2] == scoring_text[2]
                    for i in range(len(statement)-2)
                )

            if not has_scoring_text:
                self.print_warning("(sv) Has Poängsättning-section, but improper scoring text")

        if box := parse_subtask_box(path):
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
        else:
            scoring_text = [
                r"\section*{Scoring}",
                r"Your solution will be tested on a set of test groups, each worth a number of points. Each test group contains",
                r"a set of test cases. To get the points for a test group you need to solve all test cases in the test group."
            ]
            has_scoring_text = False
            with open(path, "r") as f:
                statement = [line.replace("\n", "") for line in f.readlines()]
                has_scoring_text = any(
                    statement[i] == scoring_text[0] and
                    statement[i+1] == scoring_text[1] and
                    statement[i+2] == scoring_text[2]
                    for i in range(len(statement)-2)
                )

            if not has_scoring_text:
                self.print_warning("(en) Has Scoring-section, but improper scoring text")

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
