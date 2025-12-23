from pathlib import Path
import string

from kattistools.common import get_statements, get_known_statement_names, get_language_code
from kattistools.checkers.checker import Checker
from kattistools.args import Args

def any_has(lines, needle):
    return any(needle in line for line in lines)

class CheckStatement(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("statement", path, args)

        self.handle_problem(path)

    def get_unique_lines(self, path):
        with open(path, "r") as f:
            return set(f.readlines())

    # Checks that the statement is not almost empty
    def check_statement_length(self, statement_path):
        with open(statement_path, 'r') as f:
            lines = f.readlines()
            total_len = sum(len(line) for line in lines)

        if total_len <= 100:
            self.print_warning(f"({get_language_code(statement_path)}) statement is unreasonably short ({total_len} chars)")

    def check_quotes(self, statement_path, language):
        def remove_texttt_content_multiline(path):
            with open(path, "r") as f:
                lines = f.readlines()
            """Remove all content inside \texttt{...}, including nested braces and across multiple lines."""
            result = []
            texttt_level = 0
            for line in lines:
                i = 0
                tokens = []
                while i < len(line):
                    if line.startswith(r"\texttt{", i):
                        i += len(r"\texttt{")
                        texttt_level += 1
                    elif line[i] == '{':
                        texttt_level += 1
                    elif line[i] == '}':
                        texttt_level -= 1

                    if texttt_level == 0:
                        tokens.append(line[i])
                    i += 1
                
                if tokens:
                    result.append(''.join(tokens))
            return set(result)

        lines = self.get_unique_lines(statement_path)
        texttt_free_lines = remove_texttt_content_multiline(statement_path)

        weird_quotes = ["’", "’"]
        for quote in weird_quotes:
            if any_has(lines, quote):
                self.print_error(f"({language}) Don't use {quote}")

        all_quotes = ["’", "’", "\"", "”", "''", "``"]
        for quote in all_quotes:
            if any_has(lines, f",{quote}"):
                self.print_error(f"({language}) Chatgpt error: ,{quote} occurs")
            
            if any_has(lines, f".{quote}"):
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
            if quote[0] == '\"':
                lines_used = texttt_free_lines
            else:
                lines_used = lines

            if any_has(lines_used, quote[0]):
                ln = [i for i in lines_used if i.count(quote[0])>0]
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

    def check_subsection(self, path):
        with open(path, 'r') as f:
            lines = f.readlines()
        illegal_subsections = [
            "subsection{",
            "subsection*{"
        ]
        for subsection in illegal_subsections:
            if any_has(lines, subsection):
                self.print_warning(f"({get_language_code(path)}) statement has subsection \"{subsection}" + '}", prefer "\\section*{}"')

        if any_has(lines, 'section{'):
            self.print_warning(f'({get_language_code(path)})' + r' statement has "\section{}", prefer "\section*{}"')

    def handle_all(self, path, language):
        self.check_statement_length(path)
        self.check_quotes(path, language)
        self.check_exponents(path, language)
        self.check_subsection(path)


    def get_problem_name(self, statement_path):
        with open(statement_path, 'r') as f:
            first_line = f.readlines()[0]
        try:
            problem_name = first_line.split('{')[1].split('}')[0]
        except:
            return ''
        return problem_name

    def is_capitalized(self, letter, prefer_true):
        uppercase = string.ascii_uppercase + "ÅÄÖ"
        if letter in uppercase:
            return True
        return True if prefer_true else False

    def handle_swedish(self, statement_path):
        problem_name = self.get_problem_name(statement_path)
        if not problem_name:
            self.print_warning(f'(sv) statement: missing \\problemname')
            return
        first_word = problem_name.split()[0]
        if not self.is_capitalized(first_word[0], prefer_true=True):
            self.print_error(f'(sv) First letter in problem name "{first_word}" is not capitalized')
            return
        for word in problem_name.split()[1:]:
            if self.is_capitalized(word[0], prefer_true=False) and word not in get_known_statement_names():
                self.print_info(f'(sv) First letter in word "{word}" in title is capitalized. Double-check that this is a name')

    def handle_english(self, statement_path):
        problem_name = self.get_problem_name(statement_path)
        if not problem_name:
            self.print_warning(f'(en) statement: missing \\problemname')
            return

        lowercase_words_in_title = ['a', 'an', 'the', 'and', 'but', 'for', 'or', 'so', 'yet', 'at', 'by', 'for', 'in', 'of']
        for word in problem_name.split()[1:]:
            if not self.is_capitalized(word[0], prefer_true=True) and word not in lowercase_words_in_title:
                self.print_warning(f'(en) first letter in word "{word}" is not capitalized')

    def handle_problem(self, path: Path):
        statement_path = path / 'problem_statement'
        if not statement_path.exists():
            return

        for statement in get_statements(statement_path):
            if statement.name.count(".")==1:
                self.print_error("Statement with only .tex")
            language = statement.name.split('.')[1]

            if language == 'sv':
                self.handle_swedish(statement)
            if language == 'en':
                self.handle_english(statement)

            self.handle_all(statement, language)
