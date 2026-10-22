from pathlib import Path
import re
import string

from kattistools.common import get_statements, get_known_statement_names, get_language_code
from kattistools.checkers.checker import Checker
from kattistools.args import Args

def any_has(lines, needle):
    return any(needle in line for line in lines)

def remove_texttt_content(text):
    """Remove all content inside \texttt{...}, including nested braces and across multiple lines."""
    tokens = []
    texttt_level = 0
    i = 0
    while i < len(text):
        if text.startswith(r"\texttt{", i):
            i += len(r"\texttt{")
            texttt_level += 1
            continue
        elif text[i] == '{':
            if texttt_level > 0:
                texttt_level += 1
        elif text[i] == '}':
            if texttt_level > 0:
                texttt_level -= 1
                i += 1
                continue

        if texttt_level == 0:
            tokens.append(text[i])
        i += 1
    return ''.join(tokens)

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

    def read_prose(self, statement_path):
        """The statement without comments and \\texttt (literal code), which follow no prose conventions."""
        with open(statement_path, "r") as f:
            text = f.read()
        text = re.sub(r"(?<!\\)%.*", "", text)
        return remove_texttt_content(text)

    def check_ellipsis(self, statement_path, language):
        text = self.read_prose(statement_path)
        occurrences = {m.group(0).strip() for m in re.finditer(r"[^\n]{0,20}(\.\.\.|…)", text)}
        for occurrence in sorted(occurrences):
            self.print_warning(f"({language}) Prefer \\dots over ... or …: {occurrence}")

    def check_quotes(self, statement_path, language):
        def shorten(quoted):
            quoted = ' '.join(quoted.split())
            return quoted if len(quoted) <= 60 else quoted[:57] + '...'

        # Math can't contain prose quotes, and f''(x) is a double prime
        text = self.read_prose(statement_path)
        text = re.sub(r"(?<!\\)\$\$.*?(?<!\\)\$\$", " ", text, flags=re.DOTALL)
        text = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", " ", text, flags=re.DOTALL)

        if language == "sv":
            correct_quote = ("''", "''")
            forbidden_quotes = [("``", "''")]
        elif language == "en":
            correct_quote = ("``", "''")
            forbidden_quotes = [("''", "''")]
        else:
            correct_quote = None

        # Quote-like characters that don't match the LaTeX quotes, mapped to what to use instead
        replacements = {
            "‘": "`" if language == "en" else "'",
            "’": "'",
            "´": "'",
            "′": "$'$",
            "″": "$''$",
        }
        # Correct in e.g. German or French, so only forbid them where we know the right quotes
        if correct_quote is not None:
            for quote in ["„", "‚", "«", "»"]:
                replacements[quote] = f"{correct_quote[0]}word{correct_quote[1]}"

        for quote, replacement in replacements.items():
            if quote in text:
                self.print_warning(f"({language}) Don't use {quote}, use {replacement} instead")

        # Punctuation inside the closing quote (``hello,'') looks like part of the quoted text,
        # which is confusing when the quote is e.g. an exact string to print. This includes ellipses.
        punctuation_in_quote = re.compile(r"(\S{0,20}?)(\.\.\.|…|\\l?dots(?:\{\})?|[.,;:])(''|'|[\"”’])")
        bad_endings = set()
        for m in punctuation_in_quote.finditer(text):
            before, punctuation, quote = m.groups()
            bad_endings.add((f"{before}{punctuation}{quote}", f"{before}{quote}{punctuation}"))
        for bad, good in sorted(bad_endings):
            self.print_warning(f"({language}) Put punctuation after the closing quote: write {good} instead of {bad}")

        if correct_quote is None:
            return
        forbidden_quotes += [('"', '"'), ("“", "”"), ("”", "”")]

        # In English, '' both closes correct quotes and opens forbidden ones, so drop correct pairs first
        if language == "en":
            text = re.sub(r"``.*?''", " ", text, flags=re.DOTALL)

        for open_quote, close_quote in forbidden_quotes:
            if open_quote not in text:
                continue

            pattern = re.escape(open_quote) + "(.*?)" + re.escape(close_quote)
            quoted_words = {shorten(m) for m in re.findall(pattern, text, flags=re.DOTALL)}
            # Drop matched pairs so later patterns (e.g. ”…” after “…”) don't match across them
            text = re.sub(pattern, " ", text, flags=re.DOTALL)
            if not quoted_words:
                self.print_warning(f"({language}) Don't use {open_quote}word{close_quote}, use {correct_quote[0]}word{correct_quote[1]} instead")
            for w in sorted(quoted_words):
                self.print_warning(f"({language}) Don't use {open_quote}{w}{close_quote}, use {correct_quote[0]}{w}{correct_quote[1]} instead")

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
        self.check_ellipsis(path, language)
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
        lowercase = string.ascii_lowercase + "åäö"
        if letter in uppercase:
            return True
        if letter in lowercase:
            return False
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
