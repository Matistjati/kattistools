from pathlib import Path

from kattistools.common import get_generator
from kattistools.checkers.checker import Checker
from kattistools.args import Args

class GeneratorChecker(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Check generator", path, args)
        self.handle_problem(path)

    def handle_problem(self, path):
        data_path = path / 'data'
        if not data_path.exists():
            return

        # Find the order of subtask defined in generator (order expected by author)
        gen = get_generator(data_path)
        if gen is None:
            self.print_warning("Couldn't find generator for problem")
            return

        # Check: there should be no REQUIRE_SAMPLE_REUSE
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
            return
        
        # Check: did not forget to run generator after changes
        # This is kind of fuzzy, since git does not store timestamps
        generator_change_date = gen.stat().st_mtime
        secret_change_date = secret_path.stat().st_mtime
        if generator_change_date > secret_change_date:
            self.print_error_if("Generator is newer than secret data. You should re-run the generator.",
                                [self.perform_finalization_checks])

        secret_groups = sorted(p.stem for p in secret_path.glob('*/') if p.is_dir())

        if len(secret_groups) != len(generator_group_names):
            self.print_error("Number of groups in generator and secret mismatch")
            self.print_error(f"secret: {secret_groups}, generator: {generator_group_names}")
            return
        
        if secret_groups!=generator_group_names:
            self.print_error("Order of groups in generator and secret mismatch")
            self.print_error(f"secret: {secret_groups}, gen: {generator_group_names}")

