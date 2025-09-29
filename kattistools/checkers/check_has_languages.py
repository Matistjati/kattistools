import os
from pathlib import Path

from kattistools.common import *
from kattistools.checkers.checker import Checker
import re

def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    # Create a DP table with one extra row and column
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Fill the table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1

            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost  # Substitution
            )

            # Transposition check
            if (
                i > 1 and j > 1 and
                s1[i - 1] == s2[j - 2] and
                s1[i - 2] == s2[j - 1]
            ):
                dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)  # Transposition

    return dp[m][n]


class CheckStatementLanguages(Checker):
    def __init__(self, path):
        super().__init__("statement language", path)
        self.is_interactive = False
        self.handle_problem(path)

    def handle_problem(self, path):
        if not folder_exists(path, "problem_statement"):
            self.print_error("no statement")
            return

        statement_path = Path(path) / "problem_statement"

        known = ["problem.sv.tex", "problem.en.tex", "problem.da.tex"]
        for file in statement_path.glob("*"):
            if file.name not in known:
                closest_dist = 100000
                closest_name = ""

                for name in known:
                    d = edit_distance(file.name, name)
                    if d < closest_dist:
                        closest_dist = d
                        closest_name = name
                
                if closest_dist<=3:
                    self.print_error(f"Did you misspell {file.name}? Similar to {closest_name}")

        if not (statement_path / "problem.sv.tex").exists():
            self.print_warning("problem.sv.tex is missing")


        if not (statement_path / "problem.en.tex").exists():
            self.print_warning("problem.en.tex is missing")

