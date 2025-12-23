from kattistools.common import *
from kattistools.args import Args

class Checker:
    def __init__(self, name: str, path: Path, args: Args):
        self.name = name
        self.args = args
        self.path = path
        self.errors = {}

    def print_generic(self, kind, message):
        if kind not in self.errors:
            self.errors[kind] = []
        self.errors[kind].append(message)

    def print_error(self, message):
        self.print_generic("[red]Errors:[/red]", message)

    def print_warning(self, message):
        self.print_generic("[#FFFF00]Warnings:[/#FFFF00]", message)

    def print_info(self, message):
        self.print_generic("[#75ddff]Info:[/#75ddff]", message)

    def is_po_problem(self):
        PO_repos = [
            "swedish-olympiad-",
            "egoi-qual",
            "manadens"
        ]
        for repo in PO_repos:
            if any(repo in part for part in self.path.resolve().parts):
                return True
        return self.args.programmeringsolympiden 

