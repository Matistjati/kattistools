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
    run_checkers(args, [CheckData], [], [], collect_error)
    return all_messages

def test_interaction_leading_whitespace():
    messages = collect(Path("tests/problems/interaction_whitespace/bad"))
    assert sum("whitespace after" in m for m in messages) == 1, messages

def test_interaction_no_leading_whitespace():
    messages = collect(Path("tests/problems/interaction_whitespace/good"))
    assert not any("whitespace after" in m for m in messages), messages
