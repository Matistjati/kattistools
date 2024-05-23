import os

from kattistools.common import *
from kattistools.checkers.checker import Checker

class SubtaskOrderChecker(Checker):
    def __init__(self, path):
        super().__init__("subtask order", path)
        self.handle_problem(path)

    def is_generator(self, path):
        return path.endswith(('.dsl', '.bash', '.sh'))

    def get_generator(self, files):
        for file in files:
            if self.is_generator(file):
                is_testdata_tools = False
                # Sometimes, people add a modified testdata_tools generator
                with open(file, "r") as f:
                    for line in f:
                        if line.startswith("# This file"):
                            is_testdata_tools = True
                            break
                if is_testdata_tools:
                    continue
                return file
        return None

    def handle_problem(self, path):
        if not folder_exists(path, "data"):
            self.print_warning("Did not find any secret data")
            return
        data_path = os.path.join(path,"data")
        files = get_files(data_path)

        # Find the order of subtask defined in generator (order expected by author)
        gen = self.get_generator(files)
        if gen is None:
            self.print_warning("Couldn't find generator for problem")
            return
        
        generator_group_names = []
        with open(gen, "r") as f:
            for line in f:
                if line.startswith("group"):
                    generator_group_names.append(line.split()[1])

        # Find subtasks, and order the same as kattis
        if not folder_exists(data_path, "secret"):
            self.print_warning("No secret data for problem")
            return
        secret_path = os.path.join(data_path, "secret")

        secret_groups = [get_node_name(directory) for directory in get_subdirectiories(secret_path)]
        secret_groups = sorted(secret_groups)

        if len(secret_groups) != len(generator_group_names):
            self.print_error("Number of groups in generator and secret mismatch")
            print(f"secret: {secret_groups}, generator: {generator_group_names}")
            return
        
        if secret_groups!=generator_group_names:
            self.print_error("Order of groups in generator and secret mismatch")
            print(f"secret: {secret_groups}, gen: {generator_group_names}")

