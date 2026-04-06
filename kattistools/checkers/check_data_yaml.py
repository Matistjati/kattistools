from pathlib import Path
import yaml

from kattistools.checkers.checker import Checker
from kattistools.args import Args
from kattistools.common import is_scoring_problem

class CheckDataYAML(Checker):
    def __init__(self, path: Path, args: Args):
        super().__init__("Data .yaml", path, args)
        self.handle_problem(path)

    def check_node(self, root, path):
        testdata_yaml = path / 'testdata.yaml'
        if not testdata_yaml.exists():
            self.print_error(f"'data/{testdata_yaml.relative_to(root)}' is missing")
            return
        
        with open(testdata_yaml, 'r') as f:
            problem_yaml = yaml.safe_load(f)
            if not problem_yaml:
                problem_yaml = {}

        if 'range' not in problem_yaml:
            self.print_error(f"'range' is missing in 'data/{testdata_yaml.relative_to(root)}'")
            return


    def handle_problem(self, path):
        if not is_scoring_problem(path):
            return
        
        data_root = path / 'data'
        if not data_root.exists():
            return
        
        self.check_node(data_root, data_root)
        sample_root = data_root / 'sample'
        if sample_root.exists():
            self.check_node(data_root, sample_root)

        secret_root = data_root / 'secret'
        if not secret_root.exists():
            return
        
        self.check_node(data_root, secret_root)

        subtask_dirs = list(dir for dir in secret_root.iterdir() if dir.is_dir())
        if len(subtask_dirs) == 0:
            self.print_error("No subtasks in secret")
            return
        
        for subtask_dir in subtask_dirs:
            self.check_node(data_root, subtask_dir)
            sub_subtask_dirs = list(dir for dir in subtask_dir.iterdir() if dir.is_dir())
            if len(sub_subtask_dirs) > 0:
                self.print_error(f"'{subtask_dir.relative_to(data_root)}' has recursive subtasks")
                return

