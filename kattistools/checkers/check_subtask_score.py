from pathlib import Path

from kattistools.checkers.checker import Checker
from kattistools.common import count_subtasks

class CheckScoreMatchesStatement(Checker):
    def __init__(self, path):
        super().__init__("scores match statement", path)
        self.handle_problem(path)

    def get_secret_scores(self, path: Path):
        scores = []
        for f in sorted(path.glob("*/testdata.yaml")):
            with open(f, "r") as file:
                score_line = list(filter(lambda line: line.startswith("range: "), file.readlines()))
                if len(score_line)==0:
                    self.print_error(f"range not given in {f}")
                    return
                score_range = score_line[0].split("range: ")[1]
                scores.append(int(score_range.split()[1]))
        return scores

    def get_statement_scores(self, statement_path: Path):
        statement_scores: list[list[int]] = []

        for stpath in statement_path.glob('*.tex'):
            scores = []
            with open(stpath, "r") as f:
                inside_box = False
                counter = 1
                for line in f:
                    if line.startswith(r"  \textbf{Gr"):
                        inside_box = 2
                    if inside_box < 2:
                        continue
                    if inside_box:
                        s = line.split()
                        s = [i.replace("$","") for i in s]
                        numbercnt = sum(i.isdigit() for i in s)
                        if numbercnt>1:
                            numbers = [int(i) for i in s if i.isdigit()]
                            if numbers[0]!=counter:
                                self.print_error(f"mismatch group count for {''.join(stpath.resolve().parts[-1])}. saw {numbers[0]}, expected {counter}")
                                return
                            scores.append(numbers[1])
                            counter+=1
                    if line.startswith("\\end{tabular}"):
                        inside_box = False

            statement_scores.append(scores)
        if len(statement_scores)==0:
            self.print_error(f"Did not manage to find subtask scores in {statement_path}")
            return None

        if not all(statement_scores[0]==score for score in statement_scores):
            self.print_error(f"different statements disagree on scores for {statement_path}")
            self.print_error(statement_scores)
        
        return statement_scores[0]


    def handle_problem(self, path):
        if not (path / 'data').exists():
            self.print_error("Problem has no data")
            return
        if not (path / 'data' / 'secret').exists():
            self.print_error("Problem has no secret data")
            return
        if not (path / 'problem_statement').exists():
            self.print_error("Problem has no statement")
            return

        secret_path = path / 'data' / 'secret'
        secret_scores = self.get_secret_scores(secret_path)
        if not secret_scores or len(secret_scores) == 0:
            self.print_error("No subtask scores specified in secret")
            return
        if sum(secret_scores) != 100:
            self.print_warning(f"secret: total score is not 100, is {sum(secret_scores)}")

        # We only have scoring text if we have subtasks
        if count_subtasks(path) > 1:
            statement_path = path / "problem_statement"
            statement_scores = self.get_statement_scores(statement_path)

            if statement_scores!=secret_scores:
                self.print_error("Score mismatch statement/secret")
                self.print_error(f"Secret: {secret_scores}, statement: {statement_scores}")
