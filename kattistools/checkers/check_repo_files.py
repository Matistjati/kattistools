from pathlib import Path

from kattistools.checkers.checker import Checker
from kattistools.checkers.check_files import CheckFiles
from kattistools.common import gitignored, EXCLUDED_DIRS
from kattistools.args import Args


class CheckRepoFiles(Checker):
    """Stray files that are not tied to a single problem. Runs once per git repo."""

    def __init__(self, path: Path, args: Args):
        super().__init__("Repo files", path, args)
        self.handle_repo(path)

    # Editor state, may show up anywhere in the repo
    disallowed_directories_anywhere = {
        '.vscode', '.idea'
    }

    def check_disallowed(self, path: Path):
        candidates: list[tuple[str, str]] = [] # (path relative to repo, warning)

        for dir in path.rglob('*'):
            if dir.name not in self.disallowed_directories_anywhere or not dir.is_dir():
                continue
            if any(part in EXCLUDED_DIRS for part in dir.parts):
                continue
            rel = str(dir.relative_to(path))
            candidates.append((rel, f"Directory '{rel}' exists. Remove or add to .gitignore"))

        # The same temporary files CheckFiles flags per problem, but in the repo root
        for ext in CheckFiles.disallowed_extensions:
            for file in path.glob(f'*{ext}'):
                if file.is_file():
                    candidates.append((file.name, f"Stray temporary file: '{file.name}'"))
        for file in CheckFiles.disallowed_files:
            if (path / file).is_file():
                candidates.append((file, f"Stray temporary file: '{file}'"))
        for dir in CheckFiles.disallowed_directories:
            if (path / dir).exists():
                candidates.append((dir, f"Directory '{dir}' exists. Likely temporary folder, consider removing"))

        ignored = gitignored(path, [rel for rel, _ in candidates])
        for rel, message in candidates:
            if rel not in ignored:
                self.print_warning(message)

    def handle_repo(self, path: Path):
        self.check_disallowed(path)
