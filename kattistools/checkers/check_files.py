import os
from pathlib import Path
import hashlib

from kattistools.common import get_statements
from kattistools.checkers.checker import Checker
from kattistools.args import Args

class CheckFiles(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Problem files", path, args)
        self.handle_problem(path)

    def check_input_validator(self, path):
        if not (path / 'input_validators').exists():
            if (path / 'input_format_validators').exists():
                self.print_error("input_format_validators is renamed to input_validators")
            else:
                self.print_error('Problem has no input validator')

    def check_output_validator(self, path: Path):
        if not (path / 'output_validators').exists():
            return
        
        path = path / 'output_validators'
        subdirs = [node for node in path.glob('*') if node.is_dir()]
        if len(subdirs) == 0:
            self.print_error("output_validators has no subfolder: prefer C++ output validators using the validate.h header")
            return
        if len(subdirs) > 1:
            self.print_error("Multiple output validators are not supported")
            return
        validator_dir = subdirs[0]

        validate_h = [h for h in validator_dir.glob('*.h') if h.name=="validate.h"]
        if len(validate_h) == 0:
            self.print_error("Output validator does not use validate.h")
            return

        sha256_hash = hashlib.sha256(validate_h[0].read_bytes()).hexdigest()
        data_root = Path(__file__).parent.parent.parent / "data"
        expected_validator_hash = (data_root / "output_validator_hash.txt").read_text()
        if sha256_hash != expected_validator_hash:
            self.print_warning(f"Outdated 'validate.h' in output validator. Get the newest from 'testdata_tools'")


    def check_testdata_root(self, path):
        if (path / "testdata.yaml").exists():
            self.print_error("testdata.yaml in root")

    def check_statements(self, path):
        statement_path = path / "problem_statement"
        if not (statement_path).exists():
            self.print_error("Problem has no problem statement")
            return

        if self.is_po_problem() and not (statement_path / "problem.sv.tex").exists():
            self.print_warning("'problem.sv.tex' is missing")

        if not (statement_path / "problem.en.tex").exists():
            self.print_warning("'problem.en.tex' is missing")

    def check_testdata(self, path):
        data_path = path / 'data'
        if not data_path.exists():
            self.print_error("Problem has no test data")

        if not (data_path / 'secret').exists():
            self.print_warning("'data/secret' does not exist")

        if not (data_path / 'sample').exists():
            self.print_warning("Problem has no sample test data")

    def check_timelim(self, path):
        unused_files = ['timelimit', 'memorylimit']
        for dot in ['', '.']:
            for file in unused_files:
                if (path / f"{dot}{file}").exists():
                    self.print_warning(f"Problem has {dot}{file} file, which does nothing")

    binary_extensions = {
        '.exe', '.dll', '.so', '.dylib', '.o', '.obj', '.a', '.lib',
        '.class', '.jar', '.pyc', '.pyo', '.out', '.pdb', '.ilk',
    }

    def check_no_binaries(self, path):
        for file in path.rglob('*'):
            if not file.is_file():
                continue

            if os.access(file, os.X_OK) or file.suffix.lower() in self.binary_extensions:
                try:
                    with open(file, 'rb') as f:
                        chunk = f.read(1024)
                        if b'\0' in chunk:
                            self.print_warning(f"Stray binary file: '{file.relative_to(path)}'")
                except:
                    pass

    # TODO: only complain about this if it's not in the gitignore
    # also disallow score.txt
    disallowed_extensions = { # don't push perf stuff
        '.data', '.old'
    }

    disallowed_directories = { # Artifact from test data generation
        'data_generation'
    }

    def check_disallowed(self, path):
        for ext in self.disallowed_extensions:
            for file in path.rglob(f'*{ext}'):
                if not file.is_file():
                    continue

                self.print_warning(f"Stray temporary file: '{file.relative_to(path)}'")
        
        for dir in self.disallowed_directories:
            if (path / dir).exists():
                self.print_warning(f"Directory '{dir}' exists. Likely temporary folder, consider removing")


    def handle_problem(self, path):
        self.check_testdata(path)
        self.check_input_validator(path)
        self.check_output_validator(path)
        self.check_testdata_root(path)
        self.check_statements(path)
        self.check_timelim(path)
        self.check_no_binaries(path)
        self.check_disallowed(path)
