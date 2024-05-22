
class Checker:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def print_generic(self, kind, message):
        print(f"{kind} {message} ({self.name}), at {self.path}")

    def print_error(self, message):
        self.print_generic("ERROR!", message)

    def print_warning(self, message):
        self.print_generic("warning!", message)


    def check(path):
        raise NotImplementedError
