import os

from kattistools.common import *
from kattistools.checkers.checker import Checker



def categorize_path(path):
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
    print(f"ERROR! can't find competition type for {path}")
    return "ERROR"

def get_prefix(type):
    ret = "Programmeringsolympiadens "
    return ret+type+" "

def get_year(path):
    return path.split("olympiad-")[1][0:4]


def notify_if_wrong_source(line, path):
    if line.startswith("source:"):
        comp = categorize_path(path)
        year = get_year(path)
        pref = get_prefix(comp)
        source = line.split("source:")[1].lstrip()
        if source[-1]=="\n":
            source = source[0:-1]
        if source != pref+year:
            print(f"ERROR: source '{line}', wanted             '{pref+year}'")
            print(f"For problem {path}")
            tryagain = " ".join(source.split(" ")[0:3])
            if tryagain == pref+year:
                print("Good if only first 3")
            print("****\n")


class ProblemYamlChecker(Checker):
    def __init__(self, path):
        super().__init__("problem.yaml", path)
        self.handle_problem(path)
    
    def print_maybe(self, message):
        self.print_generic("maybe change", message)

    def notify_rights_owner(self, line):
        if line.startswith("rights_owner") and line!="rights_owner: Programmeringsolympiaden":
            self.print_maybe(f"rights owner {line}")


    def handle_problem(self, path):
        # We can assume that problem.yaml exists, since that is precondition to be considred a problem
        with open(os.path.join(path, "problem.yaml"), "r") as f:
            # Did we find show_test_data_groups: true ?
            found_showtestdata = False
            # Did we find type: scoring ?
            found_scoring = False

            for line in f:
                line = line.strip()
                if line.startswith("name:"):
                    self.print_maybe(f"problem.yaml has name field: \"{line}\"")

                if line.startswith("author:"):
                    if "programmeringsolympiaden" in line.lower():
                        self.print_error(f"problem has \"programmeringsolympiaden\" listed as author")
                
                if True:
                    self.notify_rights_owner(line)

                if line.lstrip().startswith("on_reject:") or line.lstrip().startswith("range:") or line.lstrip().startswith("objective:"):
                    self.print_error(f"wrong grading {line.strip()}")

                if line.lstrip().startswith("show_test_data_groups: true") or \
                   line.lstrip().startswith("show_test_data_groups: yes"):
                    found_showtestdata=True
                
                if line.lstrip().startswith("type: scoring"):
                    found_scoring=True
                
                if True:
                    notify_if_wrong_source(line, path)
                
        if not found_showtestdata:
            self.print_error("problem.yaml needs 'show_test_data_groups: true'")

        if not found_scoring:
            self.print_error("problem.yaml needs 'type: scoring'")

