import os

from kattistools.common import *
from kattistools.checkers.checker import Checker
import re



class CheckStatement(Checker):
    def __init__(self, path):
        super().__init__("statement", path)
        self.is_interactive = False
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
        ret = []
        with open(path, "r") as f:
            for line in f:
                ret.append(line)
        return ret

    def parse_swedish_subtask_box(self, path):
        lines = self.read_file(path)
        if not self.any_begins(lines, "Din lösning kommer att testas på en mängd testfallsgrupper."):
            self.print_error("Missing poängsättning-section")
            
        if True and not self.any_has(lines, "\\textbf{Grupp}"):
            self.print_warning(f"missing modern subtask box {get_node_name(path)}")
            return
        
        if not self.any_has(lines, "Inga ytterligare begränsningar."):
            self.print_warning("Did you forget \"Inga ytterligare begränsningar.\" in subtask box?")

    def handle_swedish(self, path):
        lines = self.get_lines(path)
        if not self.is_interactive and not self.any_begins(lines, "\section*{Indata}"):
            self.print_error("missing \section*{Indata}")
        if not self.is_interactive and not self.any_begins(lines, "\section*{Utdata}"):
            self.print_error("missing \section*{Utdata}")
        
        

        no_subtasks = self.any_begins(lines, "Din lösning kommer att testas på flera testfall.")
        # If that line is present, do not look for subtask box
        if not no_subtasks:
            self.parse_swedish_subtask_box(path)
 

    def handle_english(self, path):
        lines = self.get_lines(path)
        if not self.is_interactive and not self.any_begins(lines, "\section*{Input}"):
            self.print_error("missing \section*{Input}")
        if not self.is_interactive and not self.any_begins(lines, "\section*{Output}"):
            self.print_error("missing \section*{Output}")
        
        if True and not self.any_has(lines, "\\textbf{Group}"):
            self.print_error(f"missing modern subtask box {get_node_name(path)}")

        if not self.any_has(lines, "No additional constraints."):
            self.print_warning("Did you forget \"No additional constraints.\" in subtask box?")

 
    def handle_all(self, path, language):
        lines = self.get_lines(path)
        
        forbidden_quotes = [("’","’"), ("\"","\""), ("``", "''")]
        correct_quote = ("”","”")
        if language=="sv":
            correct_quote = ("”","”")
            forbidden_quotes.append(("``", "''"))
        if language=="en":
            correct_quote = ("``", "''")
            forbidden_quotes.append(("”","”"))
        for quote in forbidden_quotes:
            if self.any_has(lines, quote[0]):
                word = [i for i in lines if i.count(quote[0])>0]
                if len(word)==0:
                    print(word)
                    self.print_error(f"Don't use {quote[0]}word{quote[1]}, use {correct_quote[0]}word{correct_quote[1]} instead")
                else:
                    word = word[0].split(quote[0])[1].split(quote[1])[0]
                    self.print_error(f"Don't use {quote[0]}{word}{quote[1]}, use {correct_quote[0]}{word}{correct_quote[1]} instead")


    def handle_problem(self, path):
        if not folder_exists(path, "problem_statement"):
            self.print_error("no statement")
            return
        
        with open(os.path.join(path,"problem.yaml"),"r") as f:
            if "interactive" in f.read():
                self.is_interactive = True
        statement_path = os.path.join(path, "problem_statement")

        statements = [file for file in get_files(statement_path) if file.endswith(".tex")]
        for statement in statements:
            name = os.path.basename(statement)
            if name.count(".")==1:
                self.print_error("Statement with only .tex")
            language = None

            if ".sv" in statement:
                language = "sv"
                self.handle_swedish(statement)
            if ".en" in statement:
                language = "en"
                self.handle_english(statement)
            self.handle_all(statement, language)

