from pathlib import Path
import subprocess
import yaml

EXCLUDED_DIRS = [".git", "testdata_tools"]


def is_problem(path: Path):
    if not (path / 'problem.yaml').exists():
        return False
    # Avoid CSES false positives
    with open(path / "problem.yaml", "r") as f:
        yaml_data = yaml.safe_load(f)
        if yaml_data and 'problem_format_version' in yaml_data and 'cses' in yaml_data['problem_format_version']:
            return False
    return True

def gather_problems(path: Path) -> list[Path]:
    problems = []
    def _directory_dfs(path: Path):
        if any(path.name.endswith(exclude) for exclude in EXCLUDED_DIRS):
            return

        if path.is_file():
            return

        if is_problem(path):
            problems.append(path)
            return

        children = path.iterdir()
        for dir in reversed(sorted(children)):
            _directory_dfs(dir)

    _directory_dfs(path)
    return problems

def gitignored(path: Path, files: list[str]) -> set[str]:
    """Return the subset of `files` (relative to `path`) that git ignores.

    Tracked files are never reported as ignored, since they will be pushed
    regardless of any ignore rule. If `path` is not inside a git repository
    (or git is unavailable) nothing is ignored."""
    if not files:
        return set()
    try:
        result = subprocess.run(
            ['git', '-C', str(path), 'check-ignore', '--stdin', '-z'],
            input=b'\0'.join(f.encode() for f in files),
            capture_output=True,
        )
    except OSError:
        return set()
    # 0: some paths ignored, 1: none ignored, 128: fatal (e.g. not a git repo)
    if result.returncode not in (0, 1):
        return set()
    return {f.decode() for f in result.stdout.split(b'\0') if f}

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

def get_generator(data_path: Path):
    for item in data_path.glob('*'):
        if is_generator(item):
            return item
    return None

def is_statement(file: Path) -> bool:
    if not file.is_file():
        return False
    if file.suffix not in {".tex", ".md"}:
        return False
    first_part = file.name.split('.')[0]
    # Fuzzy matching to allow us to give errors for misspelled statements
    if edit_distance(first_part, "problem") > 3:
        return False
    return True

def get_statements(statement_path: Path) -> list[Path]:
    statements = []
    for statement in list(statement_path.glob('*.tex')) + list(statement_path.glob('*.md')):
        if is_statement(statement):
            statements.append(statement)
    return statements

def is_interactive(path: Path):
    if not (path / 'problem.yaml').exists():
        return False
    with open(path / "problem.yaml", "r") as f:
        return "interactive" in f.read()

def is_scoring_problem(path: Path):
    if not (path / 'problem.yaml').exists():
        return False
    with open(path / "problem.yaml", "r") as f:
        return "scoring" in f.read()

def get_language_code(path):
    parts = path.name.split('.')
    if len(parts) > 1:
        return parts[1]
    raise Exception(f"Could not find language code for {path}")


# Number of subtasks according to secret
def count_subtasks(problem_path: Path):
    secret_path = problem_path / 'data' / 'secret'
    return len([path for path in secret_path.glob('*') if path.is_dir()])

def format_score(score: float) -> str:
    return str(int(score)) if float(score).is_integer() else str(score)

def format_scores(scores: list[float]) -> str:
    return "[" + ", ".join(format_score(score) for score in scores) + "]"

def has_secret_data(problem_path: Path):
    secret_path = problem_path / 'data' / 'secret'
    return secret_path.exists()

def get_known_statement_names():
    NAMES_PATH = Path(__file__).parent.parent / "data" / "names.txt"
    with open(NAMES_PATH, 'r') as f:
        names = [name.strip() for name in f.readlines()]
    return names + [f"{name}s" for name in names]

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
