from pathlib import Path

def is_problem(path: Path):
    return (path / 'problem.yaml').exists()

def is_generator(file: Path) -> bool:
    return file.is_file() and file.suffix in {".dsl", ".bash", ".sh"}

def is_interactive(problem: Path) -> bool:
    with open(problem / 'problem.yaml', 'r') as f:
        return 'interactive' in f.read()

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
