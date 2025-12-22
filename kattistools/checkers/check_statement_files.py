from pathlib import Path
import re

from kattistools.common import get_statements
from kattistools.checkers.checker import Checker
from kattistools.args import Args

class CheckStatementFiles(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Statement files", path, args)
        self.handle_problem(path)

    def check_statement_files(self, path: Path):
        if not (path / 'problem_statement').exists():
            return

        statement_path = path / "problem_statement"

        known_languages = ['sv', 'en', 'da']
        for statement in get_statements(statement_path):
            name = statement.name
            if name.count(".")==1:
                self.print_error(f"Statement name {name} lacks language code (e.g .sv)")
            pattern = r'^(problem\..+\.(tex|md))$'
            if not re.fullmatch(pattern, name):
                self.print_error(f"Statement name {name} does not match problem.<language>.md or problem.<language>.tex")
            language = re.findall(r'^problem\.(.+?)\.(tex|md)$', name)
            if language:
                lang_code = language[0][0]
                if lang_code not in known_languages:
                    self.print_warning(f"Unknown language code '{lang_code}' in statement file '{name}'")

    def handle_problem(self, path):
        self.check_statement_files(path)
