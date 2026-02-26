from pathlib import Path
import re

from kattistools.common import get_statements, get_language_code, count_subtasks
from kattistools.checkers.checker import Checker
from kattistools.args import Args
from dataclasses import dataclass

@dataclass
class SubtaskLine:
    group_index: int
    point_value: int
    constraints: str

@dataclass
class SubtaskBox:
    language: str
    subtask_lines: list[SubtaskLine]

def any_has(lines, needle):
    return any(needle in line for line in lines)

def parse_subtask_box(statement_path: Path, checker: Checker | None = None) -> SubtaskBox | None:
    if get_language_code(statement_path) not in ('sv', 'en'):
        return None
    
    with open(statement_path, 'r') as f:
        lines = f.readlines()

    lang = get_language_code(statement_path)
    HEADER_LINES = {
        "sv": r"\textbf{Grupp} & \textbf{Poäng} & \textbf{Gränser} \\ \hline",
        "en": r"\textbf{Group} & \textbf{Points} & \textbf{Constraints} \\ \hline"
    }
    HEADER_FORMAT = r"\begin{tabular}{| l | l | p{12cm} |}"
    SUBTASK_BOX_END = r"\end{tabular}"
    header_line = HEADER_LINES[lang]

    if not any_has(lines, header_line) or not any_has(lines, HEADER_FORMAT):
        if checker:
            checker.print_warning(f"({lang}) missing modern subtask box in {statement_path.name}")
        return None

    start = [i for i in range(len(lines)) if header_line in lines[i]]
    if len(start) > 1:
        if checker:
            checker.print_warning(f"({lang}) More than one subtask box")
        return None
    if len(start) == 0:
        if checker:
            checker.print_warning(f"({lang}) missing modern subtask box {statement_path.name}")
        return None
    start = start[0]
    end = [i for i in range(len(lines)) if SUBTASK_BOX_END in lines[i] and i > start]
    if len(end) == 0:
        if checker:
            checker.print_warning(f"({lang}) did not close subtask box")
        return None
    end = min(end)
    subtask_lines = lines[start+1:end]
    if len(subtask_lines) == 0:
        if checker:
            checker.print_warning(f"({lang}) Could not find any subtasks in subtask box")
        return None
    subtask_lines_parsed = []

    # Merge multilines
    merged_lines = []
    while len(subtask_lines):
        line = subtask_lines[0]
        del subtask_lines[0]
        while len(subtask_lines) and r'\hline' not in line:
            line = line[:-1]
            line += subtask_lines[0]
            del subtask_lines[0]
        merged_lines.append(line)
    subtask_lines = merged_lines    

    for line in subtask_lines:
        # $1$    & $15$  & $Q \le 10^3, N \le 10^4$ \\ \hline
        # $7$ & $38$ & Inga ytterligare begränsningar. \\ \hline % N <= 2^19 ≈ 5*10^5 eller 2^18 ≈
        pattern = re.compile(
            r'\s*\$(\d+)\$\s*&\s*\$(\d+)\$\s*&\s*(.*?)\s*\\\\\s*\\hline(?:\s*%.*)?$'
        )

        match = pattern.fullmatch(line.strip())
        if match:
            subtask_lines_parsed.append(SubtaskLine(int(match.group(1)), int(match.group(2)), match.group(3)))
        else:
            if checker:
                checker.print_warning(f"({lang}) Malformed line in subtask box: \"{line.strip()}\"")
            
            # Try to heuristically parse the line
            
            def get_first_int_and_remove_prefix(input_string):
                match = re.search(r'\d+', input_string)
                
                if match:
                    first_int = match.group(0)
                    modified_string = input_string[match.end():]
                    return first_int, modified_string
                else:
                    return None, input_string
            group, line = get_first_int_and_remove_prefix(line)
            if not group:
                continue
            points, line = get_first_int_and_remove_prefix(line)
            if '&' not in line:
                continue
            line = line.split('&')[1]
            if r'\\' not in line:
                continue
            line = line.split(r'\\')[0]
            line = line.strip()
            subtask_lines_parsed.append(SubtaskLine(int(group), int(points), line))
        
    return SubtaskBox(lang, subtask_lines_parsed)

class CheckSubtaskBox(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Subtask box", path, args)
        self.handle_problem(path)

    def handle_problem(self, path: Path):
        self.add_message_condition(self.is_po_problem)
        statement_path = path / 'problem_statement'
        if not statement_path.exists():
            return

        for statement in get_statements(statement_path):
            box = parse_subtask_box(statement, self)
            if not box:
                continue

            subtask_sum = sum(line.point_value for line in box.subtask_lines)
            if subtask_sum != 100:
                self.print_error(f"({get_language_code(statement)}) sum of subtasks in subtask box is {subtask_sum}, not 100")

            if len(box.subtask_lines) != count_subtasks(path):
                self.print_error(f"({get_language_code(statement)}) subtask box number of subtasks does not match number of subtasks in secret")

            expected_group = 1

            for line in box.subtask_lines:
                if line.group_index != expected_group:
                    self.print_error(f"({get_language_code(statement)}) subtask box has incorrect group ordering: expected {expected_group}, got {line.group_index}")

                expected_group += 1