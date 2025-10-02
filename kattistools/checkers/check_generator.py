from pathlib import Path

from kattistools.common import is_generator
from kattistools.checkers.checker import Checker

class GeneratorChecker(Checker):
    def __init__(self, path):
        super().__init__("Check generator", path)
        self.handle_problem(path)


    def get_generator(self, data_path: Path):
        for item in data_path.glob('*'):
            if is_generator(item):
                # Sometimes, people add a modified testdata_tools generator
                with open(item, "r") as f:
                    is_testdata_tools = any(line.startswith('# This file') for line in f.readlines())
                    if is_testdata_tools:
                        continue
                return item
        return None

    def handle_problem(self, path):
        data_path = path / 'data'
        if not data_path.exists():
            self.print_warning("Did not find any secret data")
            return

        # Find the order of subtask defined in generator (order expected by author)
        gen = self.get_generator(data_path)
        if gen is None:
            self.print_warning("Couldn't find generator for problem")
            return

        # Check that there is no REQUIRE_SAMPLE_REUSE
        with open(gen, "r") as f:
            for line in f:
                if line.startswith("REQUIRE_SAMPLE_REUSE=0"):
                    self.print_error("Generator has REQUIRE_SAMPLE_REUSE=0")

        generator_group_names = []
        with open(gen, "r") as f:
            for line in filter(lambda line: line.startswith("group"), f.readlines()):
                generator_group_names.append(line.split()[1])

        # Find subtasks, and order the same as kattis
        secret_path = data_path / 'secret'
        if not secret_path.exists():
            self.print_warning("No secret data for problem")
            return

        secret_groups = sorted(p.stem for p in secret_path.glob('*/') if p.is_dir())

        if len(secret_groups) != len(generator_group_names):
            self.print_error("Number of groups in generator and secret mismatch")
            self.print_error(f"secret: {secret_groups}, generator: {generator_group_names}")
            return
        
        if secret_groups!=generator_group_names:
            self.print_error("Order of groups in generator and secret mismatch")
            self.print_error(f"secret: {secret_groups}, gen: {generator_group_names}")

