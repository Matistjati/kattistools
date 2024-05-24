import os

from kattistools.common import *
from kattistools.checkers.checker import Checker




class CheckStatement(Checker):
    def __init__(self, path):
        super().__init__("statement", path)
        self.handle_problem(path)
    
    def any_begins(self, lines, needle):
        return any(line.startswith(needle) for line in lines)

    def get_lines(self, path):
        seen = set()
        
        with open(path, "r") as f:
            for line in f:
                seen.add(line)
        return seen

    def handle_swedish(self, path):
        lines = self.get_lines(path)
        if not self.any_begins(lines, "\section*{Indata}"):
            self.print_error("missing \section*{Indata}")
        if not self.any_begins(lines, "\section*{Utdata}"):
            self.print_error("missing \section*{Utdata}")

    def handle_english(self, path):
        lines = self.get_lines(path)
        if not self.any_begins(lines, "\section*{Input}"):
            self.print_error("missing \section*{Input}")
        if not self.any_begins(lines, "\section*{Output}"):
            self.print_error("missing \section*{Output}")


    def handle_problem(self, path):
        if not folder_exists(path, "problem_statement"):
            self.print_error("no statement")
            return
        statement_path = os.path.join(path, "problem_statement")

        statements = [file for file in get_files(statement_path) if file.endswith(".tex")]
        for statement in statements:
            name = os.path.basename(statement)
            if name.count(".")==1:
                self.print_error("Statement with only .tex")
            if ".sv" in statement:
                self.handle_swedish(statement)
            if ".en" in statement:
                self.handle_english(statement)

