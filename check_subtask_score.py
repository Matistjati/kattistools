import os
import subprocess
import argparse
import sys

import os

def node_exists(needle, haystack):
    return any(needle in path for path in haystack)

def get_nodes(directory):
    # List all entries in the directory
    try:
        entries = os.listdir(directory)
    except PermissionError:
        print(f"Permission denied: {directory}")
        return
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return
    return entries


def get_secret_scores(path):
    secretgroups = [os.path.join(path,entry) for entry in get_nodes(path) if os.path.isdir(os.path.join(path, entry))]
    secretgroups = sorted(secretgroups)
    scores = []
    for g in secretgroups:
        files = [entry for entry in get_nodes(g) if os.path.isfile(os.path.join(g, entry))]
        score = -1
        for f in files:
            if f.endswith("testdata.yaml"):
                with open(os.path.join(g, f), "r") as file:
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
    statements = [os.path.join(path,entry) for entry in get_nodes(path)
                  if os.path.isfile(os.path.join(path, entry)) and entry.endswith(".tex")]
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

def handle_problem(path):
    directories = [entry for entry in get_nodes(path) if os.path.isdir(os.path.join(path, entry))]

    if not node_exists("data", directories):
        print("ERROR! no data for problem {path}")
        return
    if not node_exists("problem_statement", directories):
        print("ERROR! no statement for problem {path}")
        return
    datapath = os.path.join(path,"data")
    directories = [entry for entry in get_nodes(datapath) if os.path.isdir(os.path.join(datapath, entry))]

    if not node_exists("secret", directories):
        print(f"ERROR! no secret data for problem {path}")
        return
    secretpath = os.path.join(datapath, "secret")
    secretscores = get_secret_scores(secretpath)
    
    statementpath = os.path.join(path, "problem_statement")
    statement_scores = get_statement_scores(statementpath)

    if statement_scores!=secretscores:
        print(f"ERROR! score mismatch statement/secret for {path}")
        print(f"secret: {secretscores}, statement: {statement_scores}")
        return


    #print(secretscores)
    

def walk_through_directories(directory, level=0):
    """
    Recursively walk through directories and print all files at each level.

    :param directory: The directory to start walking from.
    :param level: The current level of depth in the directory tree (used for indentation).
    """
    if directory.endswith("testdata_tools"):
        return
    entries = get_nodes(directory)

    # Separate files and directories
    files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
    directories = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]

    isproblem = node_exists("problem.yaml", files)
    if isproblem:
        #print(f"{directory} is problem")
        handle_problem(directory)
        return

    for dir in directories:
        walk_through_directories(os.path.join(directory, dir), level + 1)

# Example usage:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find Python 2 files in a directory using 2to3.')
    parser.add_argument('directory', help='Directory to search for Python 2 files')
    args = parser.parse_args()
    
    directory = args.directory
    walk_through_directories(directory)
    