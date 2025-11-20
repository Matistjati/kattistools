from pathlib import Path

def is_problem(path: Path):
    return (path / 'problem.yaml').exists()

def is_generator(file: Path) -> bool:
    if not file.is_file():
        return False
    if file.suffix not in {".dsl", ".bash", ".sh"}:
        return False
    # Skolkval generators are only temporary
    if "skolkval" in file.name:
        return False
    # Sometimes, people add a modified testdata_tools generator
    # in the data directory. This is not a generator
    with open(file, "r") as f:
        is_testdata_tools = any(line.startswith('# This file') for line in f.readlines())
        if is_testdata_tools:
            return False
    return True

def is_interactive(problem: Path) -> bool:
    with open(problem / 'problem.yaml', 'r') as f:
        return 'interactive' in f.read()

# Number of subtasks according to secret
def count_subtasks(problem_path: Path):
    secret_path = problem_path / 'data' / 'secret'
    return len([path for path in secret_path.glob('*') if path.is_dir()])

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
