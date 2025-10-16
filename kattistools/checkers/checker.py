from kattistools.common import *


class Checker:
    def __init__(self, name, path):
        self.name = name
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

