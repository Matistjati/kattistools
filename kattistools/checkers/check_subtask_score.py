from pathlib import Path

from kattistools.checkers.checker import Checker
from kattistools.checkers.check_subtask_box import parse_subtask_box
from kattistools.common import count_subtasks, get_statements, get_language_code
from kattistools.args import Args

class CheckScoreMatchesStatement(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("scores match statement", path, args)
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
        statement_languages: list[str] = []

        for stpath in get_statements(statement_path):
            box = parse_subtask_box(stpath)
            if not box:
                continue
            scores = [line.point_value for line in box.subtask_lines]
            statement_scores.append(scores)
            statement_languages.append(get_language_code(stpath))

        if len(statement_scores)==0:
            return None

        if not all(statement_scores[0]==score for score in statement_scores):
            self.print_error(f"Different statements disagree on subtask scores")
            for lang_code, scores in zip(statement_languages, statement_scores):
                self.print_error(f"\t{lang_code}: {scores}")
            return None

        return statement_scores[0]


    def handle_problem(self, path):
        self.add_message_condition(self.is_po_problem)
        if not (path / 'data').exists():
            return
        if not (path / 'data' / 'secret').exists():
            return
        if not (path / 'problem_statement').exists():
            return

        secret_path = path / 'data' / 'secret'
        secret_scores = self.get_secret_scores(secret_path)
        if not secret_scores or len(secret_scores) == 0:
            self.print_error("No subtask scores specified in secret")
            return

        if sum(secret_scores) != 100:
            self.print_warning(f"secret: total score is {sum(secret_scores)}, not 100")

        # We only have scoring text if we have subtasks
        if count_subtasks(path) > 1:
            statement_path = path / "problem_statement"
            statement_scores = self.get_statement_scores(statement_path)
            if not statement_scores:
                return

            if statement_scores != secret_scores:
                self.print_error("Score mismatch between statement and test data")
                self.print_error(f"\tSecret:       {secret_scores}")
                self.print_error(f"\tStatement(s): {statement_scores}")
