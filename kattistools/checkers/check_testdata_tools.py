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
        for testdata_tools in testdata_tools_locs:
            gen_location = testdata_tools / "gen.sh"
            if not gen_location.exists():
                self.print_error(f"testdata_tools at '{testdata_tools.relative_to(path)}' does not contain a generator")
                continue

            sha256_hash = hashlib.sha256(gen_location.read_bytes()).hexdigest()
            if sha256_hash != gen_sh_hash:
                self.print_warning(f"testdata_tools '{testdata_tools.relative_to(path)}' has an outdated generator. Pull the latest version")
