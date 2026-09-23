import os
from pathlib import Path
import yaml

from kattistools.checkers.checker import Checker
from kattistools.common import EXCLUDED_DIRS
from kattistools.args import Args

def find_duplicate_keys(text: str) -> list[tuple[str, int]]:
    """(key, line) for every mapping key that repeats an earlier key in the same mapping.
    PyYAML silently keeps only the last value of such keys."""
    duplicates = []
    visited = set()

    def walk(node):
        if node is None or id(node) in visited:
            return
        visited.add(id(node))
        if isinstance(node, yaml.MappingNode):
            seen = set()
            for key_node, value_node in node.value:
                if isinstance(key_node, yaml.ScalarNode) and key_node.value != '<<':
                    key = (key_node.tag, key_node.value)
                    if key in seen:
                        duplicates.append((key_node.value, key_node.start_mark.line + 1))
                    seen.add(key)
                walk(key_node)
                walk(value_node)
        elif isinstance(node, yaml.SequenceNode):
            for child in node.value:
                walk(child)

    for document in yaml.compose_all(text, Loader=yaml.SafeLoader):
        walk(document)
    return duplicates

class CheckYAMLDuplicateKeys(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("YAML duplicate keys", path, args)
        self.handle_problem(path)

    def handle_problem(self, path: Path):
        for root, dirs, files in os.walk(path):
            dirs[:] = sorted(d for d in dirs if not any(d.endswith(exclude) for exclude in EXCLUDED_DIRS))
            for file in sorted(files):
                if not file.endswith(('.yaml', '.yml')):
                    continue
                yaml_path = Path(root) / file
                try:
                    duplicates = find_duplicate_keys(yaml_path.read_text())
                except (yaml.YAMLError, UnicodeDecodeError, OSError):
                    # Not our job to report malformed yaml
                    continue
                for key, line in duplicates:
                    self.print_error(f"'{yaml_path.relative_to(path)}' line {line}: duplicate key '{key}', only the last value is used")
