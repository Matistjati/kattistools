from pathlib import Path
import os

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

def get_node_name(node):
    return os.path.basename(node)

def get_nodes_filter(directory, f):
    return [os.path.join(directory,entry) for entry in get_nodes(directory) if f(os.path.join(directory, entry))]

# Get all folders that are in path
def get_subdirectiories(path):
    return get_nodes_filter(path, os.path.isdir)

# Get all files that are in path
def get_files(path):
    return get_nodes_filter(path, os.path.isfile)

def folder_exists(directory, folder_name):
    return os.path.isdir(os.path.join(directory, folder_name))

def file_exists(directory, file_name):
    return os.path.isfile(os.pardir.join(directory, file_name))

def split_path(path):
    return os.path.normpath(path).split(os.path.sep)

def is_problem(path: Path):
    return (path / 'problem.yaml').exists()

# Allows insert, delete, substitution and swapping two adjacent
def edit_distance(s1, s2):
    m, n = len(s1), len(s2)

    prev = list(range(n + 1))
    curr = [0] * (n + 1)
    prev2 = None

    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + cost
            )
            if (
                i > 1 and j > 1 and
                s1[i - 1] == s2[j - 2] and
                s1[i - 2] == s2[j - 1]
            ):
                curr[j] = min(curr[j], prev2[j - 2] + 1)
        prev2, prev, curr = prev, curr, prev

    return prev[n]
