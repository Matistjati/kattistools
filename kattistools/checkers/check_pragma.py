from pathlib import Path

from kattistools.checkers.checker import Checker

PRAGMA_CHECKER_NAME = "check pragma"


class CheckPragma(Checker):
    def __init__(self, path):
        super().__init__(PRAGMA_CHECKER_NAME, path)
        self.handle_problem(path)

    # if we use
    #pragma GCC target("avx2")
    # we also need to include
    #include<bits/allocator.h>
    # to avoid compile errors in Kattis' environment
    def check_avx2(self, file):
        with open(file, "r") as f:
            lines = f.readlines()
            first_pragma = -1
            for line in lines:
                if line.startswith("#pragma GCC target") and "avx2" in line:
                    first_pragma = lines.index(line)
                    break

            if first_pragma == -1:
                return
            
            first_mitigation = 100000000
            for line in lines:
                if line.startswith("#include <bits/allocator.h>") or \
                   line.startswith("#include <bits/stdc++.h>"):
                    first_mitigation = lines.index(line)
                    break

            submission_name = Path(*file.parts[-2:])
            if first_pragma < first_mitigation:
                self.print_error(f"File '{submission_name}' uses AVX2 without #include <bits/allocator.h>")

    # Kill
    #pragma GCC optimization... 
    def check_malformed_pragma(self, file):
        with open(file, "r") as f:
            for line in f.readlines():
                if line.startswith('#pragma GCC') and 'optimization' in line:
                    submission_name = Path(*file.parts[-2:])
                    self.print_error(f"File '{submission_name}' uses #pragma GCC optimization (typo!)")


    def handle_problem(self, path):
        for file in Path(path).rglob("*.cpp"):
            self.check_avx2(file)
            self.check_malformed_pragma(file)
