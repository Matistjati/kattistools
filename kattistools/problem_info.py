import yaml
from pathlib import Path

from rich.console import Console

from kattistools.checkers.check_subtask_box import parse_subtask_box
from kattistools.common import get_generator

def count_unique_testcases(problem_path: Path) -> int:
    testdata_path = problem_path / "data"
    assert testdata_path.is_dir()
    
    num_testcases = 0
    for in_path in testdata_path.rglob("*.in"):
        if in_path.is_symlink():
            continue
        num_testcases += 1
    return num_testcases

def total_testcase_size(problem_path: Path) -> int:
    testdata_path = problem_path / "data"
    if not testdata_path.exists():
        return -1
    
    total_size = 0
    for in_path in testdata_path.rglob("*.in"):
        if in_path.is_symlink():
            continue
        total_size += in_path.stat().st_size
    return total_size

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

    # Clamp
    value = max(lo, min(value, hi))
    t = (value - lo) / (hi - lo)

    if not higher_is_better:
        t = 1 - t

    # Define nicer, non-neon endpoints
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

def format_judging_time(num_testcases: int) -> str:
    num_testcases /= 60
    color = green_red_gradient(num_testcases, 0.5, 5, higher_is_better=False)
    return f"[{color}]{num_testcases:.1f}*TL[/{color}]"

def format_testcase_size(size_bytes: int) -> str:
    size_bytes /= 1024**2
    color = green_red_gradient(size_bytes, 40, 500, higher_is_better=False)
    return f"[{color}]{size_bytes:.0f}[/{color}]"

def format_testcase_count(count: int) -> str:
    color = green_red_gradient(count, 70, 300, higher_is_better=False)
    return f"[{color}]{count}[/{color}]"

if __name__ == "__main__":
    import argparse
    import rich.box as rich_box
    from rich.table import Table

    parser = argparse.ArgumentParser(description='Show problem info')
    parser.add_argument('directory', type=Path, help='Directory to recursively scan')
    parser.add_argument('--source', help='Show source column (default: yes)', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--rights-owner', help='Show rights_owner column (default: no)', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--author', help='Show author column (default: no)', action=argparse.BooleanOptionalAction, default=False)
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

    collisions = []  # list of (problem_name, points, seen) for problems with score collisions

    for problem in get_problems(directory):
        name = problem.resolve().name

        with open(problem / "problem.yaml", 'r') as f:
            problem_yaml = yaml.safe_load(f) or {}
            source_str = problem_yaml.get('source', 'N/A')
            rights_owner_str = problem_yaml.get('rights_owner', 'N/A')
            author_str = problem_yaml.get('author', 'N/A')

        if not (problem / "data").exists():
            size_str = "?"
            tc_str = "?"
            judging_str = "?"
        else:
            tc_str = format_testcase_count(count_unique_testcases(problem))
            size_str = format_testcase_size(total_testcase_size(problem))

        unique_score_str = "N/A"
        subtask_box_langs = ("sv", "en")

        # Extract info about subtask inclusions
        generator = get_generator(problem / "data")
        with open(generator, 'r') as f:
            gen_lines = f.readlines()

        subtasks = []
        for line in gen_lines:
            if line.strip().startswith("group"):
                subtasks.append(line.strip().split()[1])

        curr_group = "UNKNOWN"
        num_subtasks = len(subtasks)
        included_matrix = [[False] * num_subtasks for _ in range(num_subtasks)]
        for line in gen_lines:
            if line.strip().startswith("group"):
                curr_group = line.strip().split()[1]
                subtasks.append(curr_group)
            if line.strip().startswith("include_group"):
                includes = line.strip().split()[1:]
                for inc in includes:
                    if inc not in subtasks:
                        continue
                    inc_index = subtasks.index(inc)
                    curr_index = subtasks.index(curr_group)
                    included_matrix[curr_index][inc_index] = True

        # transitive closure of inclusion
        for k in range(num_subtasks):
            for i in range(num_subtasks):
                for j in range(num_subtasks):
                    if included_matrix[i][k] and included_matrix[k][j]:
                        included_matrix[i][j] = True

        
        # Judging estimate: worst case = max-weight antichain (own testcases per group).
        secret_path = problem / "data" / "secret"
        group_tc_counts = [
            sum(1 for p in (secret_path / g).glob("*.in") if not p.is_symlink())
            if (secret_path / g).exists() else 0
            for g in subtasks[:num_subtasks]
        ]
        antichain_tc = max_weight_antichain(included_matrix, group_tc_counts)
        if antichain_tc > 0:
            judging_str = format_judging_time(antichain_tc)

        points = []
        for lang in subtask_box_langs:
            statement_path = problem / "problem_statement" / f"problem.{lang}.tex"
            if not statement_path.exists():
                continue
            subtask_box = parse_subtask_box(statement_path)
            if not subtask_box:
                continue
            points = [line.point_value for line in subtask_box.subtask_lines]

        if points:
            if len(points) != num_subtasks:
                included_matrix = [[False] * len(points) for _ in range(len(points))]

            seen = {}
            total = 0
            for mask in range(1, 1 << len(points)):
                feasible = True
                for i in range(len(points)):
                    for j in range(len(points)):
                        if not (mask & (1 << i)):
                            continue
                        if mask & (1 << j):
                            continue
                        if included_matrix[i][j]:
                            feasible = False
                if not feasible:
                    continue
                subset_sum = sum(points[i] for i in range(len(points)) if (mask >> i) & 1)
                seen.setdefault(subset_sum, []).append(mask)
                total += 1

            percent_unique = len(seen) / total * 100 if total else 0
            color = green_red_gradient(percent_unique, 50, 95, higher_is_better=True)
            unique_score_str = f"[{color}]{len(seen)}/{total}[/{color}]"
            if len(seen) < total:
                collisions.append((name, points, seen))

        row = [name, size_str, tc_str, judging_str, unique_score_str]
        if args.source:
            row.append(source_str)
        if args.rights_owner:
            row.append(rights_owner_str)
        if args.author:
            row.append(author_str)
        table.add_row(*row,
                      style="on grey7" if table.row_count % 2 else "")


    MAX_COLLISIONS = 6
    for prob_name, points, seen in collisions:
        console.print(f"\n[bold underline]Score collisions: {prob_name}[/bold underline]")
        bad_scores = [(score, masks) for score, masks in seen.items() if len(masks) > 1]
        for score, masks in bad_scores[:MAX_COLLISIONS]:
            console.print(f"  Sum [bold]{score}[/bold] can be achieved in {len(masks)} ways:")
            for mask in masks:
                included = [points[i] for i in range(len(points)) if (mask >> i) & 1]
                console.print(f"    - {' + '.join(str(p) for p in included)}")
        if len(bad_scores) > MAX_COLLISIONS:
            console.print(f"    ... and {len(bad_scores) - MAX_COLLISIONS} more collisions not shown")

    console.print()
    console.print("Legend")
    console.print("  [cyan]Size[/cyan]          Total size of unique input files (MB)")
    console.print("  [cyan]TC[/cyan]            Number of unique testcases")
    console.print("  [cyan]Judging time[/cyan]  Approximate worst-case judging time (max-weight antichain x TL)")
    console.print("  [cyan]Unique scores[/cyan] Fraction of attainable scores that are unique")

    console.print(table)
