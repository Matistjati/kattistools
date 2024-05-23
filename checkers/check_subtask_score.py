import os

from kattistools.common import *
from kattistools.checkers.checker import Checker

def get_secret_scores(path):
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
            print(f"ERROR: found no testdata.yaml for {path}")
            return
        scores.append(score)
    return scores

def get_statement_scores(path):
    statements = [file for file in get_files(path) if file.endswith(".tex")]
    statement_scores = []

    for stpath in statements:
        scores = []
        with open(stpath, "r") as f:
            inside_box = False
            counter = 1
            for line in f:
                if line.startswith("\\begin{tabular}"):
                    inside_box = True
                if inside_box:
                    s = line.split()
                    s = [i.replace("$","") for i in s]
                    numbercnt = sum(i.isdigit() for i in s)
                    if numbercnt>1:
                        numbers = [int(i) for i in s if i.isdigit()]
                        if numbers[0]!=counter:
                            print(f"********ERROR: mismatch group count for {path}")
                            return
                        scores.append(numbers[1])
                        counter+=1
                if line.startswith("\\end{tabular}"):
                    inside_box = False
        statement_scores.append(scores)
    good = True
    for i in statement_scores:
        good &= i==statement_scores[0]
    if not good:
        print(f"different statements disagree on scores for {path}")
    
    return statement_scores[0]

class CheckScoreMatchesStatement(Checker):
    def __init__(self, path):
        super().__init__("scores match statement", path)
        self.handle_problem(path)

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
        secretscores = get_secret_scores(secret_path)
        
        statement_path = os.path.join(path, "problem_statement")
        statement_scores = get_statement_scores(statement_path)

        if statement_scores!=secretscores:
            self.print_error("score mismatch statement/secret")
            print(f"secret: {secretscores}, statement: {statement_scores}")
            return

