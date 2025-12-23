from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_statement_po as check_statement_po
from kattistools.args import get_argparser, argparse_to_args

def test_pragma_checker():
    def check(path):
        errors = []
        def collect_error(path, e):
            nonlocal errors
            for _, value in e.items():
                errors += value

        parser = get_argparser()
        args = argparse_to_args(parser.parse_args([str(path), "--PO"]))
        directory_dfs(args, [check_statement_po.CheckStatementPO], [], collect_error)
        return errors
    bad_root = Path(__file__).parent / 'problems' / 'subtask_boxes' / 'bad'
    
    for p in ["1", "2"]:
        errs = check(bad_root / "typo_swedish" / p)
        assert 'Did you forget "Inga ytterligare begränsningar." in subtask box?' in ''.join(errs)

    for p in ["1", "2"]:
        errs = check(bad_root / "typo_english" / p)
        assert 'Did you forget "No additional constraints." in subtask box?' in ''.join(errs)

    for p in ["1", "2", "3", "4", "5"]:
        errs = check(bad_root / "ampersand" / p)
        assert 'Malformed line in subtask box:' in ''.join(errs)
