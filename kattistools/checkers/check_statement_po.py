from pathlib import Path
import re

from kattistools.common import count_subtasks
from kattistools.checkers.checker import Checker
from kattistools.args import Args


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


    def parse_swedish_subtask_box(self, path):
        if count_subtasks(self.path) == 1:
            return
        lines = read_file(path)
        if not any_begins(lines, "Din lösning kommer att testas på en mängd testfallsgrupper."):
            self.print_warning("(sv) Missing poängsättning-section")
            
        if not any_has(lines, r"  \textbf{Grupp} & \textbf{Poäng} & \textbf{Gränser} \\ \hline") or \
            not any_has(lines, r"\begin{tabular}{| l | l | p{12cm} |}"):
            self.print_warning(f"(sv) missing modern subtask box in {path.name}")
            return
        else:
            def check():
                start = [i for i in range(len(lines)) if r"\textbf{Grupp} & \textbf{Poäng} & \textbf{Gränser} \\ \hline" in lines[i]]
                if len(start) > 1:
                    self.print_warning(f"(sv) More than one subtask box")
                    return
                if len(start) == 0:
                    self.print_warning(f"(sv) missing modern subtask box {path.name}")
                    return
                start = start[0]
                end = [i for i in range(len(lines)) if r"\end{tabular}" in lines[i] and i > start]
                if len(end) == 0:
                    self.print_warning(f"(sv) did not close subtask box")
                    return
                end = min(end)
                subtask_lines = lines[start+1:end]
                for line in subtask_lines:
                    if not re.fullmatch(r'\s*\$\d+\$\s*&\s*\$\d+\$\s*&\s*.*\s*\\\\\s*\\hline', line.strip()):
                        self.print_warning(f"(sv) Malformed line in subtask box: \"{line.strip()}\"")
            check()
        
        if not any_has(lines, "Inga ytterligare begränsningar."):
            self.print_warning("(sv) Did you forget \"Inga ytterligare begränsningar.\" in subtask box?")


    def handle_swedish(self, path):
        lines = set(read_file(path))
        if not self.is_interactive_problem() and not any_begins(lines, r"\section*{Indata}"):
            self.print_error(r"(sv) missing \section*{Indata}")
        if not self.is_interactive_problem() and not any_begins(lines, r"\section*{Utdata}"):
            self.print_error(r"(sv) missing \section*{Utdata}")

        self.parse_swedish_subtask_box(path)
 

    def parse_english_subtask_box(self, path):
        if count_subtasks(self.path) == 1:
            return
        lines = read_file(path)

        if not any_begins(lines, r"\section*{Scoring}"):
            self.print_warning(r"(en) Missing \section*{Scoring}")

        if not any_begins(lines, "Your solution will be tested on a set of test groups, each worth a number of points. Each test group contains"):
            self.print_warning("(en) Missing scoring text")
        
        if not any_has(lines, r"  \textbf{Group} & \textbf{Points} & \textbf{Constraints} \\ \hline") or \
            not any_has(lines, r"\begin{tabular}{| l | l | p{12cm} |}"):
            self.print_warning(f"(en) missing modern subtask box {path.name}")
        else:
            def check():
                start = [i for i in range(len(lines)) if r"  \textbf{Group} & \textbf{Points} & \textbf{Constraints} \\ \hline" in lines[i]]
                if len(start) > 1:
                    self.print_warning(f"(en) More than one subtask box")
                    return
                if len(start) == 0:
                    self.print_warning(f"(en) missing modern subtask box {path.name}")
                    return
                start = start[0]
                end = [i for i in range(len(lines)) if r"\end{tabular}" in lines[i] and i > start]
                if len(end) == 0:
                    self.print_warning(f"(en) did not close subtask box")
                    return
                end = min(end)
                subtask_lines = lines[start+1:end]
                for line in subtask_lines:
                    if not re.fullmatch(r'\s*\$\d+\$\s*&\s*\$\d+\$\s*&\s*.*\s*\\\\\s*\\hline', line.strip()):
                        self.print_warning(f"(en) Malformed line in subtask box: \"{line.strip()}\"")
            check()
            
        
        if not any_has(lines, "No additional constraints."):
            self.print_warning("(en) Did you forget \"No additional constraints.\" in subtask box?")


    def handle_english(self, path):
        lines = set(read_file(path))
        if not self.is_interactive_problem() and not any_begins(lines, r"\section*{Input}"):
            self.print_error(r"(en) missing \section*{Input}")
        if not self.is_interactive_problem() and not any_begins(lines, r"\section*{Output}"):
            self.print_error(r"(en) missing \section*{Output}")

        self.parse_english_subtask_box(path)


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
