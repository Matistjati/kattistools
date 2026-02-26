from kattistools.common import *
from kattistools.args import Args

class Checker:
    def __init__(self, name: str, path: Path, args: Args):
        self.name = name
        self.args = args
        self.path = path
        self.errors = {}
        self.skips = {}
        self.message_conditions = []

    def add_message_condition(self, fn):
        self.message_conditions.append(fn)
    
    def remove_message_condition(self, fn):
        self.message_conditions.remove(fn)

    def print_generic(self, kind, message, extra_checks=None):
        if not self.args.all:
            for check in self.message_conditions + (extra_checks or []):
                if not check():
                    self.add_skip_note(check)
                    return
        if kind not in self.errors:
            self.errors[kind] = []
        self.errors[kind].append(message)

    def print_error(self, message):
        self.print_generic("[red]Errors:[/red]", message)

    def print_error_if(self, message, checks):
        self.print_generic("[red]Errors:[/red]", message, checks)

    def print_warning(self, message):
        self.print_generic("[#FFFF00]Warnings:[/#FFFF00]", message)

    def print_warning_if(self, message, checks):
        self.print_generic("[#FFFF00]Warnings:[/#FFFF00]", message, checks)

    def print_info(self, message):
        self.print_generic("[#75ddff]Info:[/#75ddff]", message)

    def add_skip_note(self, fn):
        known_skips = {
            self.perform_strict_checks: "strict",
            self.is_po_problem: "PO",
            self.perform_finalization_checks: "finalize"
        }
        if fn not in known_skips:
            raise Exception(f"Has not added name for function {fn}")
        name = known_skips[fn]
        if name not in self.skips:
            self.skips[name] = 0
        self.skips[name] += 1

    def is_problem(self):
        return (self.path / 'problem.yaml').exists()

    def is_po_problem(self):
        if not self.is_problem():
            return False
        PO_repos = [
            "swedish-olympiad-",
            "egoi-qual",
            "manadens"
        ]
        for repo in PO_repos:
            if any(repo in part for part in self.path.resolve().parts):
                return True
        return self.args.programmeringsolympiden 

    def is_interactive_problem(self):
        if not self.is_problem():
            return False
        
        # Quick and dirty
        with open(self.path / 'problem.yaml', 'r') as f:
            return 'interactive' in f.read()

    def perform_strict_checks(self):
        return self.args.strict

    def perform_finalization_checks(self):
        return self.args.finalize
