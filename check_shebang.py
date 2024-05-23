import os

from kattistools.common import *
import checker

class CheckPythonShebang(checker.Checker):
    def __init__(self, path):
        super().__init__("check python has shebang", path)
        self.handle_problem(path)

    def handle_problem(self, path):
        python_files = [file for file in get_files(path) if file.endswith(".py")]

        for file in python_files:
            with open(file,"r") as f:
                for line in f:
                    if not line.startswith("#!/usr/bin/python3"):
                        self.print_warning(f"py file {file} does not start with shebang #!/usr/bin/python3")
                    break
        
        for child in get_subdirectiories(path):
            self.handle_problem(child)
        