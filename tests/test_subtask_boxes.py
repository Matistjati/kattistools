from pathlib import Path

from kattistools.check_problem import directory_dfs
import kattistools.checkers.check_statement_po as check_statement_po
import kattistools.checkers.check_subtask_box as check_subtask_box
from kattistools.args import get_argparser, argparse_to_args

def test_pragma_checker():
    def check(path, checker):
        errors = []
        def collect_error(path, e):
            nonlocal errors
            for _, value in e.items():
                errors += value

        parser = get_argparser()
        args = argparse_to_args(parser.parse_args([str(path), "--PO"]))
        directory_dfs(args, [checker], [], collect_error)
        return errors
    bad_root = Path(__file__).parent / 'problems' / 'subtask_boxes' / 'bad'
    
    for p in ["1", "2"]:
        errs = check(bad_root / "typo_swedish" / p, check_statement_po.CheckStatementPO)
        assert 'Likely typo: you wrote' in ''.join(errs)

    for p in ["1", "2"]:
        errs = check(bad_root / "typo_english" / p, check_statement_po.CheckStatementPO)
        assert 'Likely typo: you wrote' in ''.join(errs)

    for p in ["1", "2", "3", "4", "5"]:
        errs = check(bad_root / "ampersand" / p, check_subtask_box.CheckSubtaskBox)
        assert 'Malformed line in subtask box:' in ''.join(errs)
