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

        self.check_sample_before_secret(path)

    def check_sample_before_secret(self, path: Path):
        # Kattis sorts all test cases by name, so every sample case name must be
        # lexicographically smaller than every secret case name for the samples
        # to run/display before the secret data.
        sample_path = path / 'data' / 'sample'
        secret_path = path / 'data' / 'secret'
        if not secret_path.exists():
            return

        def case_names(root: Path):
            return sorted({f.stem for f in root.rglob('*') if f.suffix in {'.in', '.interaction'}})

        sample_names = case_names(sample_path)
        secret_names = case_names(secret_path)
        if not sample_names or not secret_names:
            return

        if sample_names[-1] >= secret_names[0]:
            self.print_warning(
                f"Sample case '{sample_names[-1]}' is not lexicographically smaller than "
                f"secret case '{secret_names[0]}'; samples may not sort before secret data"
            )
