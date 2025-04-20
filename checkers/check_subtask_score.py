import os

from kattistools.common import *
from kattistools.checkers.checker import Checker



class CheckScoreMatchesStatement(Checker):
    def __init__(self, path):
        super().__init__("scores match statement", path)
        self.handle_problem(path)

    def get_secret_scores(self, path):
        secretgroups = get_subdirectiories(path)
        secretgroups = sorted(secretgroups)
        scores = []
        for g in secretgroups:
            files = get_files(g)
            score = -1
            for f in files:
                if f.endswith("testdata.yaml"):
                    with open(f, "r") as file:
                        for l in file:
                            if l.startswith("accept_score: "):
                                score = int(l.split("accept_score: ")[1])
                                break
            if score==-1:
                self.print_error(f"found no testdata.yaml")
                return
            scores.append(score)
        return scores

    def get_statement_scores(self, path):
        statements = [file for file in get_files(path) if file.endswith(".tex")]
        statement_scores = []

        for stpath in statements:
            scores = []
            with open(stpath, "r") as f:
                inside_box = False
                counter = 1
                for line in f:
                    if line.startswith("Din lösning kommer att testas på flera testfall. För att få 100 poäng så måste du klara alla testfall."):
                        scores.append(100)

                    if line.startswith("\\begin{tabular}"):
                        inside_box = 1
                    if inside_box == 1 and line.strip().startswith("\\hline"):
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
                                self.print_error(f"mismatch group count for {''.join(split_path(stpath)[-1])}. saw {numbers[0]}, expected {counter}")
                                return
                            scores.append(numbers[1])
                            counter+=1
                    if line.startswith("\\end{tabular}"):
                        inside_box = False

            statement_scores.append(scores)
        if len(statement_scores)==0:
            self.print_error(f"Did not manage to find subtask scores in {path}")
            return None
        good = True
        for i in statement_scores:
            good &= i==statement_scores[0]
        if not good:
            self.print_error(f"different statements disagree on scores for {path}")
            self.print_error(statement_scores)
        
        return statement_scores[0]


    def handle_problem(self, path):
        directories = [entry for entry in get_nodes(path) if os.path.isdir(os.path.join(path, entry))]

        if not folder_exists(path, "data"):
            self.print_error("no data for problem")
            return
        if not folder_exists(path, "problem_statement"):
            self.print_error("no statement for problem")
            return
        data_path = os.path.join(path,"data")

        if not folder_exists(data_path, "secret"):
            self.print_error("no secret data for problem")
            return
        secret_path = os.path.join(data_path, "secret")
        secretscores = self.get_secret_scores(secret_path)
        
        statement_path = os.path.join(path, "problem_statement")
        statement_scores = self.get_statement_scores(statement_path)

        if statement_scores!=secretscores:
            self.print_error("score mismatch statement/secret")
            self.print_error(f"secret: {secretscores}, statement: {statement_scores}")
            return

