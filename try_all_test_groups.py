#!/usr/bin/python3

# This script will run all testcases towards the validation for all testgroups,
# and report any potential testcases which could also be included in additional groups.
# Mostly written by chatgpt...

import sys
import subprocess
import os
import yaml
import concurrent.futures
import re
import resource

resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

class Colors:
  GREEN = '\033[92m'
  RED = '\033[91m'
  ORANGE = '\033[93m'
  RESET = '\033[0m'

def orange(text):
  return f"{Colors.ORANGE}{text}{Colors.RESET}"
def red(text):
  return f"{Colors.RED}{text}{Colors.RESET}"
def green(text):
  return f"{Colors.GREEN}{text}{Colors.RESET}"



if len(sys.argv) < 1:
  print("no problem name")
  exit(1)

problem = sys.argv[1]
print(problem)



# Name of the C++ source file
cpp_file = problem + "/input_validators/validator/validator.cpp"
# Name of the output executable
output_executable = '/tmp/validator.out'

# Compile the C++ file
compile_command = ['g++', cpp_file, '-o', output_executable]
compile_process = subprocess.run(compile_command, capture_output=True, text=True)

# Check if compilation was successful
if compile_process.returncode == 0:
  print("Compilation successful.")
else:
  print("Compilation failed:")
  print(compile_process.stderr)
  exit(0)

def run_validator(file, flags, group):
  run_command = [output_executable] + flags.split()
  print("validating", os.path.basename(file), "for", group)
  with open(file) as inp:
    run_process = subprocess.run(run_command, stdin=inp, capture_output=True, text=True)
    return run_process.returncode == 42

def run_validator_and_print(file, flags, group):
  run_command =  [output_executable] + flags.split()
  print(red("WARNING:"), os.path.basename(file), "not in", group)
  print("flags:", flags)
  with open(file) as inp:
    run_process = subprocess.run(run_command, stdin=inp, capture_output=True, text=True)
    print("stdout:", run_process.stdout)
    print("stderr:", run_process.stderr)
    print("returncode:", run_process.returncode)
    return run_process.returncode == 42

group_to_flags = {}
infiles = {}
infiles_path = {}

# os.walk generates the file names in a directory tree
for dirpath, dirnames, filenames in os.walk(os.path.join(problem,'data')):
  group = os.path.basename(dirpath)
  if group not in ("data", "secret"):
    group_to_flags[group] = ""
  if "testdata.yaml" in filenames:
    with open(os.path.join(dirpath,'testdata.yaml'), 'r') as file:
      # Load the YAML content
      config = yaml.safe_load(file)
      if 'input_validator_flags' in config:
        group_to_flags[group] = config['input_validator_flags']
  for file in filenames:
    if file.endswith('.in'):
      if file not in infiles:
        infiles[file] = []
      infiles[file].append(group)
      infiles_path[file] = os.path.join(dirpath,file)

#print(group_to_flags)
#print(infiles)

inputs = sorted(infiles.keys())
groups = sorted(group_to_flags.keys())
if 'sample' in groups:
  groups.remove('sample')
  groups = ['sample'] + groups

inputs = sorted(inputs, key=lambda x: (re.match(r'(\d+)\.in', x) is None, x))

data = []

def go(file, g):
  val = run_validator(infiles_path[file],group_to_flags[g],g)
  inc = 1 if g in infiles[file] else 0
  if val == inc:
    return green(("OK:Y" if val else "OK:N"))
  elif val:
    return orange("MISS")
  else:
    run_validator_and_print(infiles_path[file],group_to_flags[g],g)
    return red("BAD")

for file in inputs:
  #row = [file] + [go(file, g) for g in groups]
  with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(go, file, g) for g in groups]
    row = [file] + [future.result() for future in futures]
  data.append(row)

def print_table(data, headers):
    # Determine the width of each column
    #col_widths = [max(len(str(item)) for item in col) for col in zip(*data, headers)]
    col_widths = [len(str(item)) for item in headers]
    for item in inputs:
      col_widths[0] = max(col_widths[0],len(item))

    # Create a format string for each row
    row_format = ' | '.join(f'{{:<{width}}}' for width in col_widths)

    # Print the header
    print(row_format.format(*headers))
    print('-+-'.join('-' * width for width in col_widths))

    for i in range(1,len(col_widths)):
      col_widths[i] += 9
    row_format = ' | '.join(f'{{:<{width}}}' for width in col_widths)

    # Print each row of the data
    for row in data:
        print(row_format.format(*row))

headers = ['INPUT'] + groups
print_table(data,headers)


def count_word_occurrences(word, table):
  count = 0
  for row in table:
    for item in row:
      if word in item:
        count += 1
  return count

if count_word_occurrences("BAD", data)>0:
  print(red("BADS:" + str(count_word_occurrences("BAD", data))))
if 'sample' in groups:
  for row in data:
    del row[groups.index('sample')+1]
if count_word_occurrences("MISS", data)>0:
  print(orange("MISSES:" + str(count_word_occurrences("MISS", data))))
