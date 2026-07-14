from pathlib import Path
from kattistools.checkers.check_data import CheckData
from kattistools.check_problem import run_checkers
from kattistools.args import Args

def collect(path):
    args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    all_messages = []
    def collect_error(p, e):
        for msgs in e.values():
            all_messages.extend(msgs)
    run_checkers(args, [CheckData], [], collect_error)
    return all_messages

def test_sample_copy_not_first_in_group():
    # A content-copy ('5') and a symlink ('8') of the sample both sort after
    # the group's own case ('2'), so both should be flagged.
    messages = collect(Path("tests/problems/sample_copy_bad"))
    warnings = [m for m in messages if "Sample copy" in m]
    assert any("secret/grp/5" in m for m in warnings)
    assert any("secret/grp/8" in m for m in warnings)

def test_sample_copy_first_in_group_ok():
    # The sample copies ('0' and symlink '1') sort before the group's own
    # case ('5'), so nothing should be flagged.
    messages = collect(Path("tests/problems/sample_copy_ok"))
    assert not any("Sample copy" in m for m in messages)
