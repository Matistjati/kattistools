import os

from kattistools.common import *
from kattistools.checkers.checker import Checker




def get_prefix(type):
    ret = "Programmeringsolympiadens "
    return ret+type+" "

def get_year(path):
    return path.split("olympiad-")[1][0:4]




class ProblemYamlChecker(Checker):
    def __init__(self, path):
        super().__init__("problem.yaml", path)
        self.handle_problem(path)
    
    def any_begins(self, lines, needle):
        return any(line.startswith(needle) for line in lines)

    def any_begins_case_insensitive(self, lines, needle):
        return any(line.lower().startswith(needle.lower()) for line in lines)

    def print_maybe(self, message):
        self.print_generic("maybe change", message)

    def notify_rights_owner(self, line):
        if line.startswith("rights_owner") and line!="rights_owner: Programmeringsolympiaden":
            self.print_maybe(f"rights owner {line}")

    def categorize_path(self, path):
        competitions = {}
        competitions["skolkval/"]="skolkval"
        competitions["skol/"]="skolkval"
        competitions["onlinekval/"]="onlinekval"
        competitions["online/"]="onlinekval"
        competitions["katt/"]="KATT"
        competitions["katt1/"]="KATT"
        competitions["katt2/"]="KATT"
        competitions["katt3/"]="KATT"
        competitions["district"] = "distriktsmästerskap"
        competitions["lager/"]="lägertävling"
        competitions["final/"]="final"
        competitions["langtavling/"]="långtävling"

        for c, realc in competitions.items():
            if c in path:
                return realc
        self.print_error(f"can't find competition type for \"{split_path(path)[-2]}\"")
        return "ERROR"


    def notify_if_wrong_source(self, line, path):
        if not "swedish-olympiad" in path:
            return
        if line.startswith("source:"):
            comp = self.categorize_path(path)
            year = get_year(path)
            pref = get_prefix(comp)
            source = line.split("source:")[1].lstrip()
            if source[-1]=="\n":
                source = source[0:-1]
            if "#" in source:
                source = source.split("#")[0].strip()
            if source != pref+year:
                self.print_error(f"source is '{line.split('source: ')[1]}', want '{pref+year}'")


    def handle_problem(self, path):
        # We can assume that problem.yaml exists, since that is precondition to be considred a problem
        lines = []
        with open(os.path.join(path, "problem.yaml"), "r") as f:
            for line in f:
                line = line.strip()
                lines.append(line)
                
                if True:
                    self.notify_if_wrong_source(line, path)
        
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
