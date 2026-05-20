from pathlib import Path
from kattistools.checkers.check_files import CheckFiles
from kattistools.check_problem import run_checkers
from kattistools.args import Args

path = Path("tests/problems/binary_check")
args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)

class MyCheckFiles(CheckFiles):
    def check_no_binaries(self, path):
        print(f"check_no_binaries called with {path}")
        super().check_no_binaries(path)

def collect_error(p, e):
    print(f"COLLECT: {e}")

print("STARTING")
run_checkers(args, [MyCheckFiles], [], collect_error)
print("DONE")
