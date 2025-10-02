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
                   line.startswith("#include <bits/stdc++.h>") or \
                   line.startswith("#include <bitset>"):
                    first_mitigation = lines.index(line)
                    break

            submission_name = Path(*file.parts[-2:])
            if first_pragma < first_mitigation:
                self.print_error(f"File '{submission_name}' uses AVX2 without #include <bits/allocator.h>")

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
                    pragmas = content.split('(\"')[1]
                    pragmas = pragmas.split('\")')[0]
                    pragmas = pragmas.split(',')
                    for target in pragmas:
                        if target != target.strip():
                            self.print_error(f'File \'{submission_name}\': Target {target} has trailing or leading space and will be ignored by compiler')


    def handle_problem(self, path):
        for file in path.rglob("*.cpp"):
            self.check_avx2(file)
            self.check_malformed_pragma(file)
