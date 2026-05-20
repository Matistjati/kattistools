from pathlib import Path
from kattistools.check_problem import run_checkers
from kattistools.checkers.check_yaml import ProblemYamlChecker
from kattistools.args import Args

def get_messages_for_path(path_str):
    path = Path(path_str)
    args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    all_messages = []

    def collect_error(p, e):
        nonlocal all_messages
        for msgs in e.values():
            all_messages.extend(msgs)

    run_checkers(args, [ProblemYamlChecker], [], collect_error)
    return all_messages

def test_validation_default():
    messages = get_messages_for_path("tests/problems/validation_default")
    assert any("validation: default" in msg for msg in messages)

def test_validation_malformed_default():
    messages = get_messages_for_path("tests/problems/validation_malformed_default")
    assert any("validation: default" in msg for msg in messages)

def test_validation_custom_ok():
    # validation: custom score
    messages = get_messages_for_path("tests/problems/validation_custom")
    # Should NOT have the validation warning now
    assert not any("validation: default" in msg for msg in messages)
