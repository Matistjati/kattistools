from pathlib import Path

from kattistools.check_problem import run_checkers
from kattistools.checkers.check_data_yaml import CheckDataYAML
from kattistools.checkers.check_yaml_duplicate_keys import CheckYAMLDuplicateKeys
from kattistools.args import Args

ROOT = Path(__file__).parent / 'problems' / 'testdata_yaml'

def messages(path: Path, checker):
    args = Args(path=path, programmeringsolympiden=False, strict=False, finalize=False, all=True)
    all_messages = []
    def collect_error(p, e):
        for msgs in e.values():
            all_messages.extend(msgs)
    run_checkers(args, [checker], [], [], collect_error)
    return all_messages

def test_accept_score_ok():
    assert messages(ROOT / 'good', CheckDataYAML) == []

def test_accept_score_above_range():
    msgs = messages(ROOT / 'accept_gt_range', CheckDataYAML)
    assert len(msgs) == 1
    assert "accept_score 70 is above range '0 60' in 'data/secret/group2/testdata.yaml'" in msgs[0]

def test_duplicate_keys():
    msgs = messages(ROOT / 'duplicate_keys', CheckYAMLDuplicateKeys)
    assert len(msgs) == 3
    assert any("'problem.yaml' line 5: duplicate key 'memory'" in m for m in msgs)
    assert any("'problem.yaml' line 6: duplicate key 'source'" in m for m in msgs)
    assert any("'data/secret/group1/testdata.yaml' line 3: duplicate key 'input_validator_flags'" in m for m in msgs)

def test_no_duplicate_keys():
    assert messages(ROOT / 'good', CheckYAMLDuplicateKeys) == []
