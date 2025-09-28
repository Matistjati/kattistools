from pathlib import Path

from kattistools.checkers.checker import Checker

# if we use
#pragma GCC target("avx2")
# we also need to include
#include<bits/allocator.h>
# to avoid compile errors in Kattis' environment

class CheckPragma(Checker):
    def __init__(self, path):
        super().__init__("check pragma", path)
        self.handle_problem(path)

    def check(self, file):
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
    

    def handle_problem(self, path):
        for file in Path(path).rglob("*.cpp"):
            self.check(file)
