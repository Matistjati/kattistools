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

def walk_through_directories(directory, level=0):
    """
    Recursively walk through directories and print all files at each level.

    :param directory: The directory to start walking from.
    :param level: The current level of depth in the directory tree (used for indentation).
    """
    if directory.endswith("testdata_tools"):
        return 0
    entries = get_nodes(directory)

    ret = 0
    # Separate files and directories
    files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
    directories = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]

    isproblem = node_exists("problem.yaml", files)
    if isproblem:
        return 1

    for dir in directories:
        ret += walk_through_directories(os.path.join(directory, dir), level + 1)
    return ret

# Example usage:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find Python 2 files in a directory using 2to3.')
    parser.add_argument('directory', help='Directory to search for Python 2 files')
    args = parser.parse_args()
    
    directory = args.directory
    print(f"problem count: {walk_through_directories(directory)}")
    