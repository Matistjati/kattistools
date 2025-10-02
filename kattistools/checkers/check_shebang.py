from pathlib import Path

from kattistools.checkers.checker import Checker

# Check that all python files have #!/usr/bin/python3
class CheckPythonShebang(Checker):
    def __init__(self, path):
        super().__init__("check python has shebang", path)
        self.handle_problem(path)

    def handle_problem(self, path):
        # We don't care about generators or testdata_tools python 2/3

        for file in path.rglob('*.py'):
            if 'data' in file.resolve().parts or 'testdata_tools' in file.resolve().parts:
                continue
            with open(file,"r") as f:
                for line in f:
                    if not line.startswith("#!/usr/bin/python3") and not line.startswith("#!/usr/bin/env python3"):
                        self.print_warning(f"[green].py[/green] file '{'/'.join(file.resolve().parts[-2:])}' does not start with shebang #!/usr/bin/python3")
                    break
