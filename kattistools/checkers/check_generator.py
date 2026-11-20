from pathlib import Path
import re

from kattistools.common import get_generator, parse_generator, get_secret_group_paths
from kattistools.checkers.checker import Checker
from kattistools.args import Args

# set -e, set -euo pipefail, set -o errexit
SET_E = re.compile(r'\s*set\s+(-[a-zA-Z]*e|-o\s+errexit)')
# cd "$(dirname "$0")", matched with the double quotes removed
CD_TO_SCRIPT_DIR = re.compile(r'\s*cd\s+(--\s+)?\$\(dirname\s+(--\s+)?(\$0|\$\{BASH_SOURCE\[0\]\}|\$BASH_SOURCE)\)')

class GeneratorChecker(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Check generator", path, args)
        self.handle_problem(path)

    def handle_problem(self, path):
        data_path = path / 'data'
        if not data_path.exists():
            return

        gen = get_generator(data_path)
        if not gen:
            return
        generator = parse_generator(gen, self)
        if generator.is_skolkval_generator():
            self.print_error_if("Using skolkval generator", [self.perform_finalization_checks])

        if "sample_manual" in generator.text:
            custom_validation = (path / 'output_validators').exists()

            with open(path / "problem.yaml", "r") as f:
                config = f.read()
                custom_validation |= ('float_tolerance' in config or
                    'float_absolute_tolerance' in config or
                    'float_relative_tolerance' in config)

            if not custom_validation:
                self.print_warning("Avoid using 'sample_manual' if there is no output validator")

        if "PPATH" in generator.text:
            self.print_warning("Generator: PPATH is deprecated")

        # Check: how testdata_tools' gen.sh is included
        if generator.gen_sh_line is not None:
            lines_before = generator.text.split('\n')[:generator.gen_sh_line]
            if generator.gen_sh_path.startswith(('/', '$', '~')):
                self.print_warning(f"Generator: gen.sh is included with a non-relative path ('{generator.gen_sh_path}')")
            if not any(SET_E.match(line) for line in lines_before):
                self.print_warning("Generator: no 'set -e' before including gen.sh")
            if not any(CD_TO_SCRIPT_DIR.match(line.replace('"', '')) for line in lines_before):
                self.print_warning("Generator: no 'cd \"$(dirname \"$0\")\"' before including gen.sh")

        # Check: there should be no REQUIRE_SAMPLE_REUSE
        if not generator.is_skolkval_generator():
            for line in generator.text.splitlines():
                if line.startswith("REQUIRE_SAMPLE_REUSE=0"):
                    self.print_error("Generator has REQUIRE_SAMPLE_REUSE=0")

        # Find the order of subtask defined in generator (order expected by author)
        generator_group_names = [group.name for group in generator.groups]

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

        secret_groups = [p.name for p in get_secret_group_paths(path)]

        if len(secret_groups) != len(generator_group_names):
            self.print_error("Number of groups in generator and secret mismatch")
            self.print_error(f"secret: {secret_groups}, generator: {generator_group_names}")
            return

        if secret_groups!=generator_group_names:
            self.print_error("Order of groups in generator and secret mismatch")
            self.print_error(f"secret: {secret_groups}, gen: {generator_group_names}")

