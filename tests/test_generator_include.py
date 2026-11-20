from pathlib import Path

from kattistools.check_problem import run_checkers
from kattistools.checkers.check_generator import GeneratorChecker
from kattistools.args import Args

WARNINGS = ["non-relative path", "no 'set -e' before", "no 'cd \"$(dirname \"$0\")\"' before"]

def _messages(name: str):
    path = Path(__file__).parent / 'problems' / 'generator_include' / name
    args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    messages = []
    def collect_error(p, e):
        for msgs in e.values():
            messages.extend(msgs)
    run_checkers(args, [GeneratorChecker], [], [], collect_error)
    return ''.join(messages)

def test_generator_include_good():
    messages = _messages('good')
    for warning in WARNINGS:
        assert warning not in messages, f'Gave unwarranted warning: {warning}'

def test_generator_include_bad():
    # set -e and cd come after the include, so they do not count
    messages = _messages('bad')
    for warning in WARNINGS:
        assert warning in messages, f'Did not warn: {warning}'
