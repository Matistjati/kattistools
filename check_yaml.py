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

def categorize_path(path):
    competitions = {}
    competitions["skolkval/"]="skolkval"
    competitions["skol/"]="skolkval"
    competitions["onlinekval/"]="onlinekval"
    competitions["online/"]="onlinekval"
    competitions["katt/"]="KATT"
    competitions["katt1/"]="KATT"
    competitions["katt2/"]="KATT"
    competitions["katt3/"]="KATT"
    competitions["district"] = "distriktsmästerskap"
    competitions["lager/"]="lägertävling"
    competitions["final/"]="final"
    competitions["langtavling/"]="långtävling"

    for c, realc in competitions.items():
        if c in path:
            return realc
    print(f"ERROR! can't find competition type for {path}")

def get_prefix(type):
    ret = "Programmeringsolympiadens "
    return ret+type+" "

def get_year(path):
    return path.split("olympiad-")[1][0:4]

def handle_problem(path):
    
    with open(os.path.join(path), "r") as f:
        for line in f:
            if line.startswith("name:"):
                print(f"problem {path} has name {line}")
            if line.startswith("author:"):
                if "programmeringsolympiaden" in line.lower():
                    print(f"problem {path} has PO author")
            if line.startswith("rights_owner") and line!="rights_owner: Programmeringsolympiaden\n":
                print(f"rights owner {line} for {path}")
            continue
            if line.startswith("source:"):
                comp = categorize_path(path)
                year = get_year(path)
                pref = get_prefix(comp)
                source = line.split("source:")[1].lstrip()
                if source[-1]=="\n":
                    source = source[0:-1]
                if source != pref+year:
                    print(f"ERROR: source '{line}', wanted             '{pref+year}'")
                    print(f"For problem {path}")
                    tryagain = " ".join(source.split(" ")[0:3])
                    if tryagain == pref+year:
                        print("Good if only first 3")
                    print("****\n")
                
    #print(f"ERROR: no testdata.yaml for {path}")


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
        handle_problem(os.path.join(directory, "problem.yaml"))
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
    