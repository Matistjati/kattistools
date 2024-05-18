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

def is_generator(path):
    return path.endswith(('.dsl', '.bash', '.sh'))

def get_generator(files):
    for file in files:
        if is_generator(file):
            return file
    return None

def handle_problem(path):
    directories = [entry for entry in get_nodes(path) if os.path.isdir(os.path.join(path, entry))]

    if not node_exists("data", directories):
        print("ERROR! no data for problem {path}")
        return
    path = os.path.join(path,"data")
    files = [entry for entry in get_nodes(path) if os.path.isfile(os.path.join(path, entry))]
    directories = [entry for entry in get_nodes(path) if os.path.isdir(os.path.join(path, entry))]

    gen = get_generator(files)
    if gen is None:
        print(f"ERROR! couldn't find generator for problem {path}")
        return
    
    groupnames = []
    with open(os.path.join(path, gen), "r") as f:
        for line in f:
            if line.startswith("group"):
                groupnames.append(line.split()[1])
    #print("groupnames:", groupnames)
    if not node_exists("secret", directories):
        print(f"ERROR! no secret data for problem {path}")
        return
    secretpath = os.path.join(path, "secret")

    secretgroups = [entry for entry in get_nodes(secretpath) if os.path.isdir(os.path.join(secretpath, entry))]
    if len(secretgroups)!=len(groupnames):
        print(f"ERROR! number of groups in generator and secret mismatch for problem {path}")
        print(f"secret: {secretgroups}, gen: {groupnames}")
        return
    secretgroups = sorted(secretgroups)
    if secretgroups!=groupnames:
        print(f"ERROR! order of groups in generator and secret mismatch for problem {path}")
        print(f"secret: {secretgroups}, gen: {groupnames}")
        print("****\n\n")
        return
    return


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

    # Print files with indentation corresponding to the directory level
    #for file in files:
    #    print(f"{'  ' * level}- {file}")

    # Recursively walk through subdirectories
    for dir in directories:
        #print(f"{'  ' * level}+ {dir}")
        walk_through_directories(os.path.join(directory, dir), level + 1)

# Example usage:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find Python 2 files in a directory using 2to3.')
    parser.add_argument('directory', help='Directory to search for Python 2 files')
    args = parser.parse_args()
    
    directory = args.directory
    walk_through_directories(directory)
    