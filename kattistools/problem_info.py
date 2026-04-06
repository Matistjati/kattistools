import yaml
from pathlib import Path
from dataclasses import dataclass, field

from rich.console import Console

from kattistools.checkers.check_subtask_box import parse_subtask_box
from kattistools.common import get_generator


@dataclass
class ScoreResult:
    display: str = "N/A"
    has_collision: bool = False
    points: list[int] = field(default_factory=list)
    seen: dict = field(default_factory=dict)

@dataclass
class ProblemInfo:
    name: str
    size_mb: float | None
    distinct_tc: int | None
    total_tc: int | None
    judging: str
    score: ScoreResult
    source: str
    rights_owner: str
    author: str
    has_english_statement: bool
    languages: list[str]
    uuid: str

def count_unique_testcases(problem_path: Path) -> int:
    testdata_path = problem_path / "data"
    assert testdata_path.is_dir()
    return sum(1 for p in testdata_path.rglob("*.in") if not p.is_symlink())


def count_total_testcases(problem_path: Path) -> int:
    testdata_path = problem_path / "data"
    assert testdata_path.is_dir()
    return sum(1 for _ in testdata_path.rglob("*.in"))


def total_testcase_size(problem_path: Path) -> int:
    testdata_path = problem_path / "data"
    if not testdata_path.exists():
        return -1
    return sum(p.stat().st_size for p in testdata_path.rglob("*.in") if not p.is_symlink())


def get_problems(directory: Path):
    if directory.name == 'testdata_tools':
        return
    if (directory / 'problem.yaml').exists():
        yield directory
        return
    for item in directory.glob('*'):
        if item.is_dir():
            yield from get_problems(item)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def green_red_gradient(value: float, lo: float, hi: float, higher_is_better: bool) -> str:
    assert lo < hi
    value = max(lo, min(value, hi))
    t = (value - lo) / (hi - lo)
    if not higher_is_better:
        t = 1 - t

    red   = (200, 30, 30)
    green = (30, 180, 40)
    r = lerp(red[0], green[0], t)
    g = lerp(red[1], green[1], t)
    b = lerp(red[2], green[2], t)
    return f"#{r:02x}{g:02x}{b:02x}"


def max_weight_antichain(included_matrix: list[list[bool]], weights: list[int]) -> int:
    """Return the maximum total weight over all antichains in the inclusion DAG.
    included_matrix[i][j] = True means group i (transitively) includes group j.
    Groups in an antichain are pairwise incomparable (neither includes the other).
    """
    n = len(weights)
    best = 0
    for mask in range(1, 1 << n):
        members = [i for i in range(n) if (mask >> i) & 1]
        is_antichain = all(
            not included_matrix[i][j] and not included_matrix[j][i]
            for idx, i in enumerate(members)
            for j in members[idx + 1:]
        )
        if is_antichain:
            best = max(best, sum(weights[i] for i in members))
    return best


def colored(value: float, lo: float, hi: float, fmt: str, higher_is_better: bool) -> str:
    color = green_red_gradient(value, lo, hi, higher_is_better=higher_is_better)
    return f"[{color}]{fmt.format(value)}[/{color}]"


def parse_subtask_groups(problem: Path):
    """Parse generator file to extract subtask names and inclusion matrix."""
    generator = get_generator(problem / "data")
    if not generator:
        return None, None

    with open(generator, 'r') as f:
        gen_lines = f.readlines()

    subtasks = []
    for line in gen_lines:
        parts = line.strip().split()
        if parts and parts[0] == "group" and len(parts) >= 2:
            subtasks.append(parts[1])

    n = len(subtasks)
    included_matrix = [[False] * n for _ in range(n)]

    curr_group = None
    for line in gen_lines:
        parts = line.strip().split()
        if not parts:
            continue
        if parts[0] == "group" and len(parts) >= 2:
            curr_group = parts[1]
        elif parts[0] == "include_group" and curr_group in subtasks:
            for inc in parts[1:]:
                if inc in subtasks:
                    included_matrix[subtasks.index(curr_group)][subtasks.index(inc)] = True

    # Transitive closure
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if included_matrix[i][k] and included_matrix[k][j]:
                    included_matrix[i][j] = True

    return subtasks[:n], included_matrix


def compute_judging_estimate(problem: Path, subtasks: list[str], included_matrix: list[list[bool]]) -> str:
    secret_path = problem / "data" / "secret"
    group_tc_counts = [
        sum(1 for p in (secret_path / g).glob("*.in") if not p.is_symlink())
        if (secret_path / g).exists() else 0
        for g in subtasks
    ]
    antichain_tc = max_weight_antichain(included_matrix, group_tc_counts)
    if antichain_tc > 0:
        return colored(antichain_tc / 60, 0.5, 5, "{:.1f}*TL", higher_is_better=False)
    return "?"




def compute_score_uniqueness(problem: Path, subtasks: list[str], included_matrix: list[list[bool]]) -> ScoreResult:
    num_subtasks = len(subtasks)
    points = []
    for lang in ("sv", "en"):
        statement_path = problem / "problem_statement" / f"problem.{lang}.tex"
        if not statement_path.exists():
            continue
        subtask_box = parse_subtask_box(statement_path)
        if not subtask_box:
            continue
        points = [line.point_value for line in subtask_box.subtask_lines]

    if not points:
        return ScoreResult()

    if len(points) != num_subtasks:
        included_matrix = [[False] * len(points) for _ in range(len(points))]

    seen = {}
    total = 0
    for mask in range(1, 1 << len(points)):
        feasible = all(
            not included_matrix[i][j]
            for i in range(len(points)) if (mask & (1 << i))
            for j in range(len(points)) if not (mask & (1 << j))
        )
        if not feasible:
            continue
        subset_sum = sum(points[i] for i in range(len(points)) if (mask >> i) & 1)
        seen.setdefault(subset_sum, []).append(mask)
        total += 1

    percent_unique = len(seen) / total * 100 if total else 0
    display = colored(percent_unique, 50, 95, f"{len(seen)}/{total}", higher_is_better=True)
    return ScoreResult(display=display, has_collision=len(seen) < total, points=points, seen=seen)




def collect_problem_info(problem: Path) -> ProblemInfo:
    name = problem.resolve().name

    with open(problem / "problem.yaml", 'r') as f:
        problem_yaml = yaml.safe_load(f) or {}

    if (problem / "data").exists():
        size_mb = total_testcase_size(problem) / 1024**2
        distinct_tc = count_unique_testcases(problem)
        total_tc = count_total_testcases(problem)
    else:
        size_mb = None
        distinct_tc = None
        total_tc = None

    subtasks, included_matrix = parse_subtask_groups(problem)
    if subtasks is not None:
        judging = compute_judging_estimate(problem, subtasks, included_matrix)
        score = compute_score_uniqueness(problem, subtasks, included_matrix)
    else:
        judging = "?"
        score = ScoreResult()

    statement_dir = problem / "problem_statement"
    languages = sorted(
        p.stem.split(".")[1]
        for p in statement_dir.glob("problem.*.tex")
        if len(p.stem.split(".")) == 2
    ) if statement_dir.exists() else []

    return ProblemInfo(
        name=name,
        size_mb=size_mb,
        distinct_tc=distinct_tc,
        total_tc=total_tc,
        judging=judging,
        score=score,
        source=problem_yaml.get('source', 'N/A'),
        rights_owner=problem_yaml.get('rights_owner', 'N/A'),
        author=problem_yaml.get('author', 'N/A'),
        has_english_statement=(problem / "problem_statement" / "problem.en.tex").exists(),
        languages=languages,
        uuid=problem_yaml.get('uuid', 'N/A'),
    )


def print_collisions(console: Console, problems: list[ProblemInfo], max_shown: int = 6):
    for info in problems:
        if not info.score.has_collision:
            continue
        console.print(f"\n[bold underline]Score collisions: {info.name}[/bold underline]")
        bad_scores = [(score, masks) for score, masks in info.score.seen.items() if len(masks) > 1]
        for score, masks in bad_scores[:max_shown]:
            console.print(f"  Sum [bold]{score}[/bold] can be achieved in {len(masks)} ways:")
            for mask in masks:
                included = [info.score.points[i] for i in range(len(info.score.points)) if (mask >> i) & 1]
                console.print(f"    - {' + '.join(str(p) for p in included)}")
        if len(bad_scores) > max_shown:
            console.print(f"    ... and {len(bad_scores) - max_shown} more collisions not shown")


def add_table_row(table, info: ProblemInfo, args) -> None:
    size_str  = colored(info.size_mb,    40,  500, "{:.0f}", higher_is_better=False) if info.size_mb    is not None else "?"
    dtc_str   = colored(info.distinct_tc, 70, 300, "{}",     higher_is_better=False) if info.distinct_tc is not None else "?"
    ttc_str   = colored(info.total_tc,   250, 600, "{}",     higher_is_better=False) if info.total_tc   is not None else "?"

    row = [info.name, size_str, dtc_str, ttc_str, info.judging, info.score.display]
    if args.source:
        row.append(info.source)
    if args.rights_owner:
        row.append(info.rights_owner)
    if args.author:
        row.append(info.author)
    if args.english_statement:
        row.append("[green]Yes[/green]" if info.has_english_statement else "[red]No[/red]")
    if args.lang:
        row.append(", ".join(info.languages) if info.languages else "N/A")
    if args.uuid:
        row.append(info.uuid)
    table.add_row(*row, style="on grey7" if table.row_count % 2 else "")


if __name__ == "__main__":
    import argparse
    import rich.box as rich_box
    from rich.table import Table

    parser = argparse.ArgumentParser(description='Show problem info')
    parser.add_argument('directory', type=Path, help='Directory to recursively scan')
    parser.add_argument('--source', help='Show source column (default: yes)', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--rights-owner', help='Show rights_owner column (default: no)', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--author', help='Show author column (default: no)', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--english-statement', help='Show whether problem.en.tex exists (default: no)', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--lang', help='Show statement languages column (default: no)', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--uuid', help='Show uuid column (default: no)', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--all', help='Show all columns', action='store_true')
    args = parser.parse_args()

    if args.all:
        args.rights_owner = True
        args.author = True
        args.english_statement = True
        args.lang = True
        args.uuid = True

    console = Console()

    directory = Path(args.directory)
    if not directory.exists():
        console.print(f"[red]Error[/red]: folder {directory} does not exist")
        exit(1)

    problems = [collect_problem_info(p) for p in get_problems(directory)]

    table = Table(
        box=rich_box.ROUNDED,
        header_style="bold bright_cyan",
        border_style="bright_black",
        title_style="bold white",
        show_lines=False,
        expand=False,
    )
    table.add_column("Problem", style="bold white", no_wrap=True)
    table.add_column("Size", justify="right", no_wrap=True)
    table.add_column("D-TC", justify="right", no_wrap=True)
    table.add_column("T-TC", justify="right", no_wrap=True)
    table.add_column("Judging", justify="right", no_wrap=True)
    table.add_column("Scores", justify="right", no_wrap=True)
    if args.source:
        table.add_column("Source", justify="left", no_wrap=True)
    if args.rights_owner:
        table.add_column("Rights Owner", justify="left", no_wrap=True)
    if args.author:
        table.add_column("Author", justify="left", no_wrap=True)
    if args.english_statement:
        table.add_column("EN", justify="center", no_wrap=True)
    if args.lang:
        table.add_column("Languages", justify="left", no_wrap=True)
    if args.uuid:
        table.add_column("UUID", justify="left", no_wrap=True)

    print_collisions(console, problems)

    for info in problems:
        add_table_row(table, info, args)

    console.print()
    console.print("Legend")
    console.print("  [cyan]Size[/cyan]          Total size of unique input files (MB)")
    console.print("  [cyan]D-TC[/cyan]          Number of distinct (non-symlink) testcases")
    console.print("  [cyan]T-TC[/cyan]          Total number of testcases (including symlinks)")
    console.print("  [cyan]Judging time[/cyan]  Approximate worst-case judging time (max-weight antichain x TL)")
    console.print("  [cyan]Unique scores[/cyan] Fraction of attainable scores that are unique")

    console.print(table)
