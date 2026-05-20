from pathlib import Path
from kattistools.checkers.check_files import CheckFiles
from kattistools.check_problem import run_checkers
from kattistools.args import Args

def test_check_files_binary():
    path = Path("tests/problems/binary_check")
    args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    
    all_messages = []
    def collect_error(p, e):
        nonlocal all_messages
        for msgs in e.values():
            all_messages.extend(msgs)

    run_checkers(args, [CheckFiles], [], collect_error)
    print(f"DEBUG: messages = {all_messages}")

    # Check that binary_file is flagged
    assert any("binary_file" in msg for msg in all_messages)

    # Check that script.sh is NOT flagged as binary
    assert not any("script.sh" in msg for msg in all_messages)

    # Check that text_file is NOT flagged
    assert not any("text_file" in msg for msg in all_messages)

    # Check that .git/git_binary is NOT flagged
    assert not any("git_binary" in msg for msg in all_messages)
