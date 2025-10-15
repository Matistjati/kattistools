from pathlib import Path

from kattistools.common import is_interactive
from kattistools.checkers.checker import Checker

class CheckStatement(Checker):
    def __init__(self, path):
        super().__init__("statement", path)
        self.is_interactive = is_interactive(path)
        self.handle_problem(path)

    def any_has(self, lines, needle):
        return any(needle in line for line in lines)

    def get_unique_lines(self, path):
        with open(path, "r") as f:
            return set(f.readlines())

    # Checks that the statement is not almost empty
    # and that no line is too long
    # Allow long lines in subtask box
    def check_statement_length(self, statement_path, language):
        with open(statement_path, 'r') as f:
            lines = f.readlines()
            total_len = sum(len(line) for line in lines)

            def ignore_line(line):
                if line.startswith('\illustration'):
                    return True

                if line.strip().startswith('\item') and len(line) < 170:
                    return True
                if line.strip().startswith('\caption') and len(line) < 150:
                    return True
                line = line.strip()
                if len(line) < 3:
                    return False
                if line[0] == '$' and line[2] == '$' and line[1].isnumeric():
                    return True
                return False

            filtered_lines = filter(lambda line: not ignore_line(line), lines)
            longest_line = max(len(line) for line in filtered_lines)

        if total_len <= 100:
            self.print_warning(f"({language}) statement is unreasonably short ({total_len} chars)")
        if longest_line > 130:
            self.print_warning(f"({language}) statement has a line of length {longest_line}, which is longer than recommended max of 130")

    def check_quotes(self, statement_path, language):
        lines = self.get_unique_lines(statement_path)

        weird_quotes = ["’", "’"]
        for quote in weird_quotes:
            if self.any_has(lines, quote):
                self.print_error(f"({language}) Don't use {quote}")

        all_quotes = ["’", "’", "\"", "”", "''", "``"]
        for quote in all_quotes:
            if self.any_has(lines, f",{quote}"):
                self.print_error(f"({language}) Chatgpt error: ,{quote} occurs")
            
            if self.any_has(lines, f".{quote}"):
                self.print_error(f"({language}) Chatgpt error: .{quote} occurs")

        forbidden_quotes = [("’","’"), ("\"","\""), ("”", "”")]
        if language=="sv":
            correct_quote = ("''","''")
            forbidden_quotes.append(("``", "''"))
        elif language=="en":
            correct_quote = ("``", "''")
            forbidden_quotes.append(("''","''"))
        else:
            return

        for quote in forbidden_quotes:
            if self.any_has(lines, quote[0]):
                ln = [i for i in lines if i.count(quote[0])>0]
                if len(ln)==0:
                    self.print_error(f"({language}) Don't use {quote[0]}word{quote[1]}, use {correct_quote[0]}word{correct_quote[1]} instead")

                unique_w = set()
                for w in ln:
                    wl = quote[0].join(w.split(quote[0])[1:])

                    if wl.count(quote[1]) == 0:
                        continue
                    word = wl.split(quote[1])[0]

                    if correct_quote[0] in word:
                        continue
                    unique_w.add(word)

                for w in unique_w:
                    self.print_error(f"({language}) Don't use {quote[0]}{w}{quote[1]}, use {correct_quote[0]}{w}{correct_quote[1]} instead")

    # Check for 10^18 and similar
    def check_exponents(self, statement_path, language):
        lines = self.get_unique_lines(statement_path)
        import string
        disallowed_ends = [*string.digits]

        def check_line(line):
            while '$' in line:
                first_occ = line.find('$')
                second_occ = line.find('$', first_occ+1)
                math_content = line[first_occ+1:second_occ]
                if second_occ==-1:
                    line=''
                else:
                    line = line[second_occ+1:]
                original_math = math_content

                while '^' in math_content:
                    pow_occ = math_content.find('^')
                    math_content = math_content[pow_occ+1:]
                    # Assume proper placement if they thought of {
                    if len(math_content) == 0 or math_content[0] == '{':
                        continue

                    if len(math_content)>1:
                        if math_content[1] in disallowed_ends:
                            self.print_warning(f'({language}) statement: you probably forgot to add brackets around ^ content in math block ${original_math}$')
                            return

        for line in lines:
            check_line(line)

    def handle_all(self, path, language):
        self.check_statement_length(path,language)
        self.check_quotes(path, language)
        self.check_exponents(path, language)

    def handle_problem(self, path: Path):
        statement_path = path / 'problem_statement'
        if not statement_path.exists():
            self.print_error("Problem has no statement")
            return

        statements = statement_path.glob('*.tex')
        for statement in statements:
            if statement.name.count(".")==1:
                self.print_error("Statement with only .tex")
            language = statement.name.split('.')[1]
            self.handle_all(statement, language)#
