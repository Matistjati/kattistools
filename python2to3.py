import os
import subprocess
import argparse
import sys

def is_python2(file_path):
    try:
        # Run the 2to3 tool on the file
        result = subprocess.run(['2to3', file_path],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(str(result))
        # Check if 2to3 suggests any changes
        if "No changes" in result.stderr.decode():
            return False
        print(result.stderr.decode())
        #print(str(result.stdout))
        
        return True
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return False

def is_data_folder(file_path):
    if "/data" in file_path:
        return True
    return False

def find_python2_files(directory):
    python2_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if not is_data_folder(file_path) and is_python2(file_path):
                    #print("fix ", file_path, "?")
                    #y = input("y/n")
                    python2_files.append(file_path)
                    #if y=="y":
                    #    result = subprocess.run(['2to3', "-w", "--nobackup", file_path],
                    #            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return python2_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find Python 2 files in a directory using 2to3.')
    parser.add_argument('directory', help='Directory to search for Python 2 files')
    args = parser.parse_args()
    
    directory = args.directory
    python2_files = find_python2_files(directory)
    
    if python2_files:
        print("Python 2 files found:")
        for file in python2_files:
            print(file)
    else:
        print("No Python 2 files found.")
