from pathlib import Path

from kattistools.checkers.checker import Checker
from kattistools.args import Args

class CheckData(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Data", path, args)
        self.handle_problem(path)

    def handle_problem(self, path: Path):
        sample_path = path / 'data' / 'sample'
        if not sample_path.exists():
            return

        for statement_file in sorted(list(sample_path.glob('*.ans')) + list(sample_path.glob('*.interaction'))):
            lines = statement_file.read_text().splitlines()
            for line in lines:
                if len(line) and line[-1].isspace():
                    self.print_warning(f"Sample file '{statement_file.relative_to(path)}' has trailing whitespace")
