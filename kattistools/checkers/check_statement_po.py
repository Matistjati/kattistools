from pathlib import Path

from kattistools.common import is_interactive, count_subtasks
from kattistools.checkers.checker import Checker

class CheckStatementPO(Checker):
    def __init__(self, path):
        super().__init__("PO statement", path)
        self.problem_path = path
        self.is_interactive = is_interactive(path)
        self.handle_problem(path)

    def any_begins(self, lines, needle):
        return any(line.startswith(needle) for line in lines)

    def any_has(self, lines, needle):
        return any(needle in line for line in lines)

    def get_lines(self, path):
        seen = set()
        
        with open(path, "r") as f:
            for line in f:
                seen.add(line)
        return seen
    
    def read_file(self, path):
        with open(path, "r") as f:
            return f.readlines()

    def parse_swedish_subtask_box(self, path):
        if count_subtasks(self.problem_path) == 1:
            return
        lines = self.read_file(path)
        if not self.any_begins(lines, "Din lösning kommer att testas på en mängd testfallsgrupper."):
            self.print_warning("(sv) Missing poängsättning-section")
            
        if not self.any_has(lines, r"  \textbf{Grupp} & \textbf{Poäng} & \textbf{Gränser} \\ \hline") or \
            not self.any_has(lines, r"\begin{tabular}{| l | l | p{12cm} |}"):
            self.print_warning(f"(sv) missing modern subtask box in {path.name}")
            return
        
        if not self.any_has(lines, "Inga ytterligare begränsningar."):
            self.print_warning("(sv) Did you forget \"Inga ytterligare begränsningar.\" in subtask box?")

    def handle_swedish(self, path):
        lines = self.get_lines(path)
        if not self.is_interactive and not self.any_begins(lines, r"\section*{Indata}"):
            self.print_error(r"(sv) missing \section*{Indata}")
        if not self.is_interactive and not self.any_begins(lines, r"\section*{Utdata}"):
            self.print_error(r"(sv) missing \section*{Utdata}")

        self.parse_swedish_subtask_box(path)
 
    def parse_english_subtask_box(self, path):
        if count_subtasks(self.problem_path) == 1:
            return
        lines = self.read_file(path)

        if not self.any_begins(lines, r"\section*{Scoring}"):
            self.print_warning(r"(en) Missing \section*{Scoring}")

        if not self.any_begins(lines, "Your solution will be tested on a set of test groups, each worth a number of points. Each test group contains"):
            self.print_warning("(en) Missing scoring text")
        
        if not self.any_has(lines, r"  \textbf{Group} & \textbf{Points} & \textbf{Constraints} \\ \hline") or \
            not self.any_has(lines, r"\begin{tabular}{| l | l | p{12cm} |}"):
            self.print_warning(f"(en) missing modern subtask box {path.name}")
        
        if not self.any_has(lines, "No additional constraints."):
            self.print_warning("(en) Did you forget \"No additional constraints.\" in subtask box?")

    def handle_english(self, path):
        lines = self.get_lines(path)
        if not self.is_interactive and not self.any_begins(lines, r"\section*{Input}"):
            self.print_error(r"(en) missing \section*{Input}")
        if not self.is_interactive and not self.any_begins(lines, r"\section*{Output}"):
            self.print_error(r"(en) missing \section*{Output}")

        self.parse_english_subtask_box(path)


    def handle_problem(self, path):
        statement_path = path / 'problem_statement'
        if not statement_path.exists():
            self.print_error("No statement")
            return

        statements = statement_path.glob('*.tex')
        for statement in statements:

            if ".sv" in statement.name:
                self.handle_swedish(statement)
            if ".en" in statement.name:
                self.handle_english(statement)
