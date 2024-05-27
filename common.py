
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
