import hashlib
from pathlib import Path

from kattistools.checkers.checker import Checker
from kattistools.args import Args

class CheckInputValidator(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Input validator", path, args)
        self.handle_problem(path)

    def get_cpp_input_validator(self, path):
        for item in path.iterdir():
            if item.is_dir():
                if (item / 'validator.h').exists():
                    return item / 'validator.h'
        return None

    def handle_problem(self, path):
        input_validators = path / 'input_validators'
        if not input_validators.exists():
            return
        
        validator_h = self.get_cpp_input_validator(input_validators)
        if validator_h is None:
            self.print_error("Problem has no C++ input validator")
            return

        sha256_hash = hashlib.sha256(validator_h.read_bytes()).hexdigest()
        data_root = Path(__file__).parent.parent.parent / "data"
        expected_validator_hash = (data_root / "validator_hash.txt").read_text()
        if sha256_hash != expected_validator_hash:
            self.print_warning(f"Outdated 'validator.h' in input validator. Get the newest from 'testdata_tools'")

        # Doing it this way, we kill off build files
        directory_content = list(validator_h.parent.iterdir())
        assert validator_h in directory_content
        directory_content.remove(validator_h)
        directory_content = [item for item in directory_content if not item.name.endswith('.out')]

        if len(directory_content) == 0:
            self.print_warning("Input validator only contains 'validator.h'")
            return
        if len(directory_content) > 1:
            self.print_error("Input validator contains more files than 'validator.h' and input validator")
            return

        cpp_file = directory_content[0]
        if not cpp_file.name.endswith('.cpp'):
            self.print_error(f"No .cpp file in input validator")
            return

        cpp_contents = cpp_file.read_text()
        if '#include <bits/stdc++.h>' in cpp_contents:
            self.print_warning(f"Input validator uses '#include <bits/stdc++.h>', which is slow")
        if 'Eof()' in cpp_contents:
            self.print_warning(f"Input validator uses 'Eof()', is no longer needed")
