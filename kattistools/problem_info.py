import yaml
from pathlib import Path
from dataclasses import dataclass, field

from rich.console import Console

from kattistools.checkers.check_subtask_box import parse_subtask_box
from kattistools.common import get_generator


def count_unique_testcases(problem_path: Path) -> int:
    testdata_path = problem_path / "data"
    assert testdata_path.is_dir()
    return sum(1 for p in testdata_path.rglob("*.in") if not p.is_symlink())


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


@dataclass
class ScoreResult:
    display: str = "N/A"
    has_collision: bool = False
    points: list[int] = field(default_factory=list)
    seen: dict = field(default_factory=dict)


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


def print_collisions(console: Console, collisions: list, max_shown: int = 6):
    for prob_name, points, seen in collisions:
        console.print(f"\n[bold underline]Score collisions: {prob_name}[/bold underline]")
        bad_scores = [(score, masks) for score, masks in seen.items() if len(masks) > 1]
        for score, masks in bad_scores[:max_shown]:
            console.print(f"  Sum [bold]{score}[/bold] can be achieved in {len(masks)} ways:")
            for mask in masks:
                included = [points[i] for i in range(len(points)) if (mask >> i) & 1]
                console.print(f"    - {' + '.join(str(p) for p in included)}")
        if len(bad_scores) > max_shown:
            console.print(f"    ... and {len(bad_scores) - max_shown} more collisions not shown")


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
    args = parser.parse_args()

    console = Console()

    directory = Path(args.directory)
    if not directory.exists():
        console.print(f"[red]Error[/red]: folder {directory} does not exist")
        exit(1)

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
    table.add_column("TC", justify="right", no_wrap=True)
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

    collisions = []

    for problem in get_problems(directory):
        name = problem.resolve().name

        with open(problem / "problem.yaml", 'r') as f:
            problem_yaml = yaml.safe_load(f) or {}

        judging_str = "?"
        unique_score_str = "N/A"

        if not (problem / "data").exists():
            size_str = "?"
            tc_str = "?"
        else:
            tc_str = colored(count_unique_testcases(problem), 70, 300, "{}", higher_is_better=False)
            size_str = colored(total_testcase_size(problem) / 1024**2, 40, 500, "{:.0f}", higher_is_better=False)

        subtasks, included_matrix = parse_subtask_groups(problem)
        if subtasks is not None:
            judging_str = compute_judging_estimate(problem, subtasks, included_matrix)
            score = compute_score_uniqueness(problem, subtasks, included_matrix)
            unique_score_str = score.display
            if score.has_collision:
                collisions.append((name, score.points, score.seen))

        row = [name, size_str, tc_str, judging_str, unique_score_str]
        if args.source:
            row.append(problem_yaml.get('source', 'N/A'))
        if args.rights_owner:
            row.append(problem_yaml.get('rights_owner', 'N/A'))
        if args.author:
            row.append(problem_yaml.get('author', 'N/A'))
        if args.english_statement:
            has_en = (problem / "problem_statement" / "problem.en.tex").exists()
            row.append("[green]Yes[/green]" if has_en else "[red]No[/red]")
        table.add_row(*row, style="on grey7" if table.row_count % 2 else "")

    print_collisions(console, collisions)

    console.print()
    console.print("Legend")
    console.print("  [cyan]Size[/cyan]          Total size of unique input files (MB)")
    console.print("  [cyan]TC[/cyan]            Number of unique testcases")
    console.print("  [cyan]Judging time[/cyan]  Approximate worst-case judging time (max-weight antichain x TL)")
    console.print("  [cyan]Unique scores[/cyan] Fraction of attainable scores that are unique")

    console.print(table)
