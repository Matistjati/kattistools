from pathlib import Path

from kattistools.checkers.checker import Checker
from kattistools.args import Args

# Check that the template is not too long
class CheckCPPTemplate(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("check C++ template", path, args)
        self.handle_problem(path)

    def handle_problem(self, path):        
        for file in path.rglob('*.cpp'):
            with open(file,"r") as f:
                num_defines = len(list(filter(lambda line: line.startswith('#define'), f.readlines())))
                if num_defines >= 10:
                    self.print_warning_if(f"C++ file '{'/'.join(file.resolve().parts[-2:])}' has a too large template (more than 10 defines)",
                                          [self.perform_strict_checks])
