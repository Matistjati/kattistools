from pathlib import Path
import yaml

from kattistools.checkers.checker import Checker
from kattistools.common import edit_distance

class ProblemYamlChecker(Checker):
    def __init__(self, path):
        super().__init__("problem.yaml", path)
        self.handle_problem(path)

    def any_begins_case_insensitive(self, lines, needle):
        return any(line.lower().startswith(needle.lower()) for line in lines)

    def get_contest_source(self, path: Path):
        competitions = {}
        competitions["skolkval"]="skolkval"
        competitions["skol"]="skolkval"
        competitions["onlinekval"]="onlinekval"
        competitions["online"]="onlinekval"
        competitions["katt"]="KATT"
        competitions["katt1"]="KATT"
        competitions["katt2"]="KATT"
        competitions["katt3"]="KATT"
        competitions["district"] = "distriktsmästerskap"
        competitions["lager"]="lägertävling"
        competitions["final"]="final"
        competitions["langtavling"]="långtävling"

        for c, realc in competitions.items():
            if c in path.resolve().parts:
                return realc
        self.print_error(f"can't find competition type for \"{path.resolve().parts[-2]}\"")
        return None

    def get_contest_year(self, path: Path):
        for part in path.resolve().parts:
            if part.startswith("swedish-olympiad-"):
                return part.split("swedish-olympiad-")[1]
        self.print_error(f"Couldn't determine contest year for \"{path.resolve().parts[-2]}\"")
        return None

    def check_source_PO(self, lines, path: Path):
        is_po = any("swedish-olympiad" in part for part in path.resolve().parts)
        # We only know the source "should be" for PO
        if not is_po:
            return
        for line in filter(lambda line: line.startswith("source:"), lines):
            source = self.get_contest_source(path)
            if not source:
                return
            year = self.get_contest_year(path)
            if not year:
                return
            
            desired_source = f"Programmeringsolympiadens {source} {year}"
            yaml_source = line.split("source:")[1].strip()
            # Sometimes, there's a comment of where it's really from
            if "#" in yaml_source:
                yaml_source = yaml_source.split("#")[0].strip()
            if yaml_source != desired_source:
                self.print_error(f"source is '{yaml_source}', want '{desired_source}'")


    def check_rights_owner(self, yaml):
        # If there is no owner, we should change it to PO
        if 'rights_owner' in yaml:
            desired_rights_owner = 'Programmeringsolympiaden'
            yaml_rights_owner = yaml['rights_owner']
            if desired_rights_owner != yaml_rights_owner and edit_distance(desired_rights_owner, yaml_rights_owner) <= 3:
                self.errors(f"Likely typo: rights_owner is {yaml_rights_owner}, not {desired_rights_owner}")
        else:
            self.print_warning("No rights_owner given: should be \"rights_owner: Programmeringsolympiaden\"")

    def handle_problem(self, path):
        # We can assume that problem.yaml exists, since that is precondition to be considred a problem
        lines = []
        with open(path / "problem.yaml", "r") as f:
            lines = list(map(lambda line: line.strip(), f.readlines()))
        with open(path / "problem.yaml", "r") as f:
            problem_yaml = yaml.safe_load(f)
            if not problem_yaml:
                problem_yaml = {}

        self.check_source_PO(lines, path)
        self.check_rights_owner(problem_yaml)

        # "yes" meaning true is removed in newer yaml versions
        if self.any_begins_case_insensitive(lines, "show_test_data_groups: yes") or \
           self.any_begins_case_insensitive(lines, "show_test_data_groups:yes"):
            self.print_error("show_test_data_groups should be \"true\", not \"yes\"")

        has_test_data_groups = False
        if 'grading' in problem_yaml:
            if 'show_test_data_groups' in problem_yaml['grading']:
                if problem_yaml['grading']['show_test_data_groups'] == True:
                    has_test_data_groups = True

        if not has_test_data_groups:
            self.print_error("Missing grading: show_test_data_groups: true in problem.yaml")


        # Forbid name until the new problem format
        forbidden_keys = ["name", "on_reject", "range", "objective"]
        for key in forbidden_keys:
            if key in problem_yaml:
                self.print_error(f"problem.yaml should not have field {key}")

        disallowed_author_special_chars = [
            '/', '\\', '<', '>', '$', '"', "'",
            '?', '*', '|', ':', ';', '@', '#', '!'
        ]
        if 'author' in problem_yaml:
            author_name = problem_yaml['author']
            if author_name.lower() == 'programmeringsolympiaden':
                self.print_error("Having programmeringsolympiaden as author is bad practice (problem.yaml)")
            for char in disallowed_author_special_chars:
                if char in author_name:
                    self.print_error(f"Problem author should not contain {char}")
            if '&' in author_name:
                self.print_error('Use comma to separate author names, not &')

        is_scoring = False
        if 'type' in problem_yaml:
            if 'scoring' in problem_yaml['type']:
                is_scoring=True

        if not is_scoring:
            self.print_error("problem.yaml must have 'type: scoring'")
