from pathlib import Path

from kattistools.checkers.checker import Checker
from kattistools.args import Args

class CheckData(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Data", path, args)
        self.handle_problem(path)

    def handle_problem(self, path: Path):
        sample_path = path / 'data' / 'sample'
        if not sample_path.exists():
            return

        for statement_file in sorted(list(sample_path.glob('*.ans')) + list(sample_path.glob('*.interaction'))):
            lines = statement_file.read_text().splitlines()
            for line in lines:
                if len(line) and line[-1].isspace():
                    self.print_warning(f"Sample file '{statement_file.relative_to(path)}' has trailing whitespace")

        self.check_sample_copies_sort_first(path)

    def check_sample_copies_sort_first(self, path: Path):
        # One should do include_group sample as good hygiene
        # Because kattis sorts test cases within a group by their name such as 1.in, g2-10.in
        # instead of sample/1.in and secret/g2/g2-10.in, samples can sometimes appears last in a group,
        # which is misleading in the UI
        #
        # Detect non-symlink cases by checking for content equality,
        # using the fact that samples ought to be small for performance gains
        data_path = path / 'data'
        sample_path = data_path / 'sample'
        secret_path = data_path / 'secret'
        if not sample_path.exists() or not secret_path.exists():
            return

        exts = {'.in', '.interaction'}
        sample_resolved = set()
        sample_by_size = {}
        for f in sample_path.rglob('*'):
            if f.suffix in exts and f.is_file():
                sample_resolved.add(f.resolve())
                sample_by_size.setdefault(f.stat().st_size, []).append(f.read_bytes())

        def is_sample_copy(f: Path) -> bool:
            if f.is_symlink() and f.resolve() in sample_resolved:
                return True
            try:
                size = f.stat().st_size
            except OSError:
                # Broken symlink, not a copy
                return False
            contents = sample_by_size.get(size)
            return contents is not None and f.read_bytes() in contents

        # Group cases by their containing directory; each directory is a group.
        groups = {}
        for f in secret_path.rglob('*'):
            if f.suffix in exts and (f.is_file() or f.is_symlink()):
                groups.setdefault(f.parent, []).append(f)

        for group_dir, files in groups.items():
            copies = [f.stem for f in files if is_sample_copy(f)]
            others = [f.stem for f in files if f.stem not in copies]
            if not copies or not others:
                continue
            smallest_other = min(others)
            for stem in copies:
                if stem >= smallest_other:
                    self.print_warning(
                        f"Sample copy '{(group_dir / stem).relative_to(path)}' is not "
                        f"lexicographically smaller than the rest of its group "
                        f"(e.g. case '{smallest_other}'); it will not sort first"
                    )
