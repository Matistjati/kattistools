from pathlib import Path
import re
import subprocess
import yaml
from dataclasses import dataclass

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

SOURCES_GEN_SH = re.compile(r'\s*(?:\.|source)\s+(\S*gen\.sh)\b')

def is_generator(file: Path) -> bool:
    if not file.is_file():
        return False
    if file.suffix not in {".dsl", ".bash", ".sh"}:
        return False
    with open(file, "r") as f:
        lines = f.readlines()
    # Sometimes, people add a modified testdata_tools generator
    # in the data directory. This is not a generator
    if any(line.startswith('# This file') for line in lines):
        return False
    # A real generator sources testdata_tools' gen.sh. Example such:
    # . ../../gen.sh
    return any(SOURCES_GEN_SH.match(line) for line in lines)

def get_generator(data_path: Path) -> Path | None:
    assert data_path.name == 'data'
    generators = sorted([p for p in data_path.glob('*') if is_generator(p)])
    if len(generators) == 0:
        return None
    if len(generators) == 1:
        return generators[0]
    # Assume we only hit this path if problem has both generator.sh and generator_skolkval.sh
    if not (data_path / 'secret').exists(): # generator.sh comes first lexicographically
        return generators[0]
    secret_group_names = [p.name for p in get_secret_group_paths(data_path.parent)]
    secret_group_scores = [get_secret_group_score(p) for p in get_secret_group_paths(data_path.parent)]
    scored_generators = []
    for generator in generators:
        parsed_gen = parse_generator(generator)
        if not parsed_gen:
            continue
        group_names = [group.name for group in parsed_gen.groups]
        group_scores = [group.score for group in parsed_gen.groups]
        num_matches = 0
        if group_names == secret_group_names:
            num_matches += 1
            if group_scores == secret_group_scores:
                num_matches += 1
        scored_generators.append((num_matches, generator))

    return max(scored_generators, key=lambda t: t[0])[1]

def problem_uses_skolkval_data(problem_root: Path):
    if gen := get_generator(problem_root / 'data'):
        if parsed_gen := parse_generator(gen):
            return parsed_gen.is_skolkval_generator()
    return False


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


@dataclass
class GeneratorGroup:
    name: str
    score: int | None
    includes: list[str]

@dataclass
class Generator:
    path: Path
    text: str
    groups: list[GeneratorGroup]
    # Where testdata_tools' gen.sh is included: 0-based line index and the path as written
    gen_sh_line: int | None
    gen_sh_path: str | None

    def is_skolkval_generator(self):
        return self.path.name == 'generator_skolkval.sh'

def parse_generator(file: Path, checker: "Checker | None" = None) -> Generator:
    assert file.exists()
    with open(file, "r") as f:
        generator_text = f.read()
    groups = []
    group = None
    for line in generator_text.split('\n'):
        toks = line.split()
        if len(toks):
            if toks[0] == "group":
                if group:
                    groups.append(group)
                    group = None
                score = None
                if len(toks) == 1:
                    if checker:
                        checker.print_error("Malformed generator: contains line with only 'group'")
                    continue # Give up trying to parse this group
                elif len(toks) == 2:
                    if checker:
                        checker.print_warning("Malformed generator: contains group without score")
                    group_name = toks[1]
                else:
                    group_name = toks[1]
                    try:
                        score = int(toks[2])
                    except:
                        if checker:
                            checker.print_warning(f"Malformed generator: failed to parse group score {toks[2]} as int")

                group = GeneratorGroup(group_name, score, [])
            elif toks[0] == 'include_group':
                if group:
                    for included_group in toks[1:]:
                        if any(group.name == included_group for group in groups) or included_group == 'sample':
                            group.includes.append(included_group)
                        else:
                            if checker:
                                checker.print_error(f"Malformed generator: group {group.name} includes group {included_group} that is not yet defined")
                else:
                    if checker:
                        checker.print_error("Malformed generator: has 'include_group' before first group definition")
    if group:
        groups.append(group)

    gen_sh_line, gen_sh_path = None, None
    for i, line in enumerate(generator_text.split('\n')):
        if m := SOURCES_GEN_SH.match(line):
            gen_sh_line, gen_sh_path = i, m.group(1).strip('"\'')
            break
    return Generator(file, generator_text, groups, gen_sh_line, gen_sh_path)


# Number of subtasks according to secret
def get_secret_group_paths(problem_path: Path) -> list[Path]:
    secret_path = problem_path / 'data' / 'secret'
    return list(sorted([path for path in secret_path.glob('*') if path.is_dir()]))

def get_secret_group_score(group_path: Path) -> int | None:
    yaml_path = group_path / 'testdata.yaml'
    if not yaml_path.exists():
        return None
    with open(yaml_path, 'r') as f:
        for line in f.readlines():
            if line.startswith('accept_score'):
                toks = line.split(': ')
                if len(toks) == 2:
                    try:
                        return int(toks[1])
                    except Exception:
                        ...
    return None

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
