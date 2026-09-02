from pathlib import Path

from kattistools.checkers.checker import Checker
from kattistools.args import Args

PRAGMA_CHECKER_NAME = "check pragma"


class CheckPragma(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__(PRAGMA_CHECKER_NAME, path, args)
        self.handle_problem(path)

    # Historically, there was a check for the following bug: gcc.gnu.org/bugzilla/show_bug.cgi?id=109753
    # This was fixed in GCC 15, and Kattis now uses >=15.2. Check exists in git history

    # Check that we don't have
    #pragma GCC optimization...
    # Or
    #pragma GCC target("avx2, bmi") (bmi will not work)
    def check_malformed_pragma(self, file):
        submission_name = Path(*file.parts[-2:])
        with open(file, "r") as f:
            for line in f.readlines():
                if line.startswith('#pragma GCC') and 'optimization' in line:
                    self.print_error(f"File '{submission_name}' uses #pragma GCC optimization (typo!)")
                if line.startswith('#pragma GCC target'):
                    content = line.split('#pragma GCC target')[1]
                    if content.count('\"') > 2:
                        self.print_error(f"File '{submission_name}': Keep all targets in a single comment like this: #pragma GCC target(\"avx2,aes\")")
                        continue
                    if '("' not in content:
                        continue
                    pragmas = content.split('(\"')[1]
                    pragmas = pragmas.split('\")')[0]
                    pragmas = pragmas.split(',')
                    for target in pragmas:
                        if target != target.strip():
                            self.print_error(f'File \'{submission_name}\': Target {target} has trailing or leading space and will be ignored by compiler')


    def handle_problem(self, path):
        for file in path.rglob("*.cpp"):
            self.check_malformed_pragma(file)
