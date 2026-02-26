from pathlib import Path

from rich.console import Console

from kattistools.checkers.check_subtask_box import parse_subtask_box
from kattistools.common import get_generator
from kattistools.args import Args, parse_cmdline_args

def count_unique_testcases(problem_path: Path) -> int:
    testdata_path = problem_path / "data"
    if not testdata_path.exists():
        return -1
    
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
            get_problems(item)

def testcase_num_info(num_testcases: int) -> str:
    if num_testcases >= 45:
        return f"{num_testcases/60:.1f}*TL minutes judging time worst case"
    return f"{num_testcases}*TL second of judging time worst case"


if __name__ == "__main__":
    console = Console()
    args: Args = parse_cmdline_args()

    directory = args.path
    if not Path(directory).exists():
        console.print(f"[red]Error[/red]: folder {directory} does not exist")
        exit(1)

    for problem in get_problems(directory):
        console.print(f"[bold underline]Problem: {problem.resolve().name}[/bold underline]")
        num_testcases = count_unique_testcases(problem)
        if num_testcases < 0:
            console.print(f"could not determine number of testcases")
        else:
            def format_size(size_bytes):
                if size_bytes == 0:
                    return "0B"
                import math
                size_name = ("B", "KB", "MB", "GB", "TB")
                i = int(math.floor(math.log(size_bytes, 1024)))
                p = math.pow(1024, i)
                s = round(size_bytes / p, 2)
                return f"{s} {size_name[i]}"
            testcase_size = total_testcase_size(problem)
            console.print(f"{format_size(testcase_size)} data over {num_testcases} unique testcases. {testcase_num_info(num_testcases)}")

        subtask_box_langs = ("sv", "en")
        for lang in subtask_box_langs:
            statement_path = problem / "problem_statement" / f"problem.{lang}.tex"
            if statement_path.exists():
                subtask_box = parse_subtask_box(statement_path)
                if not subtask_box:
                    continue
                points = [line.point_value for line in subtask_box.subtask_lines]

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

                if len(points) != num_subtasks:
                    included_matrix = [[False] * len(points) for _ in range(len(points))]

                seen = {}
                total = 0
                for mask in range(1, 1 << len(points)):
                    feasible = True
                    # Only failure mode is if A succeeds, B fails, but A includes B
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

                    subset_sum = 0
                    for i in range(len(points)):
                        if (mask >> i) & 1:
                            subset_sum += points[i]
                    if subset_sum not in seen:
                        seen[subset_sum] = []
                    seen[subset_sum].append(mask)
                    total += 1
                console.print(f"Subtask sums are such that {len(seen)}/{total} ({len(seen)/total*100:.3f}%) of possible scores are unique")
                for score, masks in seen.items():
                    if len(masks) > 1:
                        console.print(f"Sum {score} can be achieved in the following ways:")
                        for mask in masks:
                            included = [i for i in range(len(points)) if (mask >> i) & 1]
                            console.print(f"  - {' '.join(str(points[i]) for i in included)}")

                break
        console.print()
