from pathlib import Path
import hashlib

from kattistools.checkers.checker import Checker
from kattistools.common import is_problem
from kattistools.args import Args


class TestdataToolsChecker(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("testdata_tools", path, args)
        self.handle_repo(path)

    def gather_problems(self, path: Path):
        problems = []
        for item in path.glob('*'):
            if is_problem(item):
                problems.append(item)
        return problems

    def handle_repo(self, path):
        testdata_tools_locs = list(path.glob('**/testdata_tools'))
        if len(testdata_tools_locs) > 1:
            locations = [f"'{p.relative_to(path)}'" for p in testdata_tools_locs][:2]
            self.print_error(f"Multiple testdata_tools in same repo. Located at {', '.join(locations)}")

        data_root = Path(__file__).parent.parent.parent / "data"
        gen_sh_hash = (data_root / "generator_hash.txt").read_text()
        input_val_hash = (data_root / "input_validator_hash.txt").read_text()
        output_val_hash = (data_root / "output_validator_hash.txt").read_text()
        for testdata_tools in testdata_tools_locs:
            for loc, hash in (('gen.sh', gen_sh_hash),
                              ('input_validators/validator/validator.h', input_val_hash),
                              ('output_validators/validator/validate.h', output_val_hash)):
                location = testdata_tools / loc
                if not location.exists():
                    self.print_warning(f"testdata_tools at '{testdata_tools.relative_to(path)}' is broken or outdated. Pull the latest version from 'git@github.com:Kodsport/testdata_tools.git'")
                    break

                sha256_hash = hashlib.sha256(location.read_bytes()).hexdigest()
                if sha256_hash != hash:
                    self.print_warning(f"testdata_tools '{testdata_tools.relative_to(path)}' is outdated. Pull the latest version from 'git@github.com:Kodsport/testdata_tools.git'")
                    break

            if (testdata_tools / '.git').exists():
                self.print_warning(f"testdata_tools '{testdata_tools.relative_to(path)}' is a git repo. Delete its .git folder")

            if (testdata_tools / 'examples').exists():
                self.print_info('testdata_tools has examples folder. Consider removing')

            
