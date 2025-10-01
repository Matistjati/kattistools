from pathlib import Path

from kattistools.checkers.checker import Checker

class ProblemYamlChecker(Checker):
    def __init__(self, path):
        super().__init__("problem.yaml", path)
        self.handle_problem(path)
    
    def any_begins(self, lines, needle):
        return any(line.startswith(needle) for line in lines)

    def any_begins_case_insensitive(self, lines, needle):
        return any(line.lower().startswith(needle.lower()) for line in lines)

    def notify_rights_owner(self, line):
        if line.startswith("rights_owner") and line!="rights_owner: Programmeringsolympiaden":
            self.print_maybe(f"rights owner {line}")

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
            if c in path.parts:
                print(c)
                return realc
        self.print_error(f"can't find competition type for \"{path.parts[-2]}\"")
        return None

    def get_contest_year(self, path: Path):
        for part in path.parts:
            if part.startswith("swedish-olympiad-"):
                return part.split("swedish-olympiad-")[1]
        self.print_error(f"Couldn't determine contest year for \"{path.parts[-2]}\"")
        return None

    def check_source_PO(self, lines, path):
        is_po = any("swedish-olympiad" in part for part in path.parts)
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


    def check_rights_owner(self, lines, path: Path):
        # If there is no owner, we should change it to PO
        if any(line.startswith("rights_owner") for line in lines):
            return
        self.print_warning("No rights_owner given: should be \"rights_owner: Programmeringsolympiaden\'")

    def handle_problem(self, path):
        # We can assume that problem.yaml exists, since that is precondition to be considred a problem
        path = Path(path)
        lines = []
        with open(path / "problem.yaml", "r") as f:
            lines = list(map(lambda line: line.strip(), f.readlines()))

        self.check_source_PO(lines, path)
        self.check_rights_owner(lines, path)

        if not self.any_begins(lines, "show_test_data_groups: true") and \
           not self.any_begins(lines, "show_test_data_groups: yes"):
            self.print_error("problem.yaml must have 'show_test_data_groups: true'")

        forbidden_keys = ["name:", "on_reject:", "range:", "objective:"]
        for key in forbidden_keys:
            if self.any_begins(lines, key):
                self.print_error(f"problem.yaml should not have field {key[:-1]}")

        if self.any_begins_case_insensitive(lines, "author: programmeringsolympiaden") or \
           self.any_begins_case_insensitive(lines, "author:programmeringsolympiaden"):
            self.print_error("problem.yaml, having programmeringsolympiaden as author is bas practice")


        if not self.any_begins(lines, "type: scoring"):
            self.print_error("problem.yaml must have 'type: scoring'")

        for line in lines:
            if line.startswith("author:") and "&" in line:
                self.print_error("Use comma to separate author names, not &")
