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

def test_sample_not_lex_smaller_than_secret():
    # sample case '5' is not lexicographically smaller than secret case '1'
    messages = collect(Path("tests/problems/sample_lex_order"))
    assert any("lexicographically smaller" in msg for msg in messages)

def test_sample_lex_smaller_than_secret_ok():
    # sample case '1' is lexicographically smaller than secret case '2'
    messages = collect(Path("tests/problems/sample_lex_order_ok"))
    assert not any("lexicographically smaller" in msg for msg in messages)
