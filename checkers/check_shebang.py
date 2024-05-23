import os

from kattistools.common import *
from kattistools.checkers.checker import Checker

class CheckPythonShebang(Checker):
    def __init__(self, path):
        super().__init__("check python has shebang", path)
        self.handle_problem(path)

    def handle_problem(self, path):
        # We don't care about generator python 2/3
        if path.endswith("data"):
            return
        python_files = [file for file in get_files(path) if file.endswith(".py")]

        for file in python_files:
            with open(file,"r") as f:
                for line in f:
                    if not line.startswith("#!/usr/bin/python3") and not line.startswith("#!/usr/bin/env python3"):
                        self.print_warning(f"py file {file} does not start with shebang #!/usr/bin/python3")
                    break
        
        for child in get_subdirectiories(path):
            self.handle_problem(child)
        