import itertools
import json
import runpy
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Selfie with Python" / "Selfie_with_Python.py"
RESULTS = ROOT / "work" / "R35-T023" / "inputs_expected_actual.json"

ESCAPE = 27
SPACE = 32
OTHER = 0
KEY_SEQUENCES = [
    tuple(prefix) + (ESCAPE,)
    for prefix in itertools.chain.from_iterable(
        itertools.product((OTHER, SPACE), repeat=length) for length in range(5)
    )
][:20]


def expected_saves(keys):
    saved = []
    for key in keys:
        if key % 256 == ESCAPE:
            break
        if key % 256 == SPACE:
            saved.append(f"Selfie_{len(saved)}.jpg")
    return saved


def expected_reads(keys):
    for index, key in enumerate(keys, start=1):
        if key % 256 == ESCAPE:
            return index
    return len(keys)


@pytest.fixture(scope="session")
def scenario_results():
    results = []
    yield results
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


def make_cv2(keys, fail_read_at=None):
    key_index = 0
    saved = []
    shown = []
    state = {"release_calls": 0, "destroy_calls": 0, "read_calls": 0}

    class FakeCamera:
        def read(self):
            read_index = state["read_calls"]
            state["read_calls"] += 1
            if read_index == fail_read_at:
                return False, None
            return True, f"frame-{read_index}"

        def release(self):
            state["release_calls"] += 1

    def wait_key(_delay):
        nonlocal key_index
        key = keys[key_index]
        key_index += 1
        return key

    fake_cv2 = SimpleNamespace(
        VideoCapture=lambda index: (state.update(camera_index=index) or FakeCamera()),
        namedWindow=lambda name: state.update(window_name=name),
        imshow=lambda name, frame: shown.append((name, frame)),
        waitKey=wait_key,
        imwrite=lambda name, frame: saved.append((name, frame)) or True,
        destroyAllWindows=lambda: state.update(destroy_calls=state["destroy_calls"] + 1),
    )
    return fake_cv2, saved, shown, state


def run_script(monkeypatch, keys, fail_read_at=None):
    fake_cv2, saved, shown, state = make_cv2(keys, fail_read_at)
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    sleeps = []
    monkeypatch.setattr(time, "sleep", sleeps.append)
    runpy.run_path(str(SCRIPT))
    state["sleeps"] = sleeps
    return saved, shown, state


@pytest.mark.parametrize(
    "keys",
    KEY_SEQUENCES,
    ids=lambda keys: "-".join(map(str, keys)),
)
def test_small_key_sequences_match_independent_oracle(
    keys, monkeypatch, capsys, scenario_results
):
    saved, shown, state = run_script(monkeypatch, keys)
    expected = {
        "saved_files": expected_saves(keys),
        "read_calls": expected_reads(keys),
        "release_calls": 1,
        "destroy_calls": 1,
    }
    actual = {
        "saved_files": [filename for filename, _frame in saved],
        "read_calls": state["read_calls"],
        "release_calls": state["release_calls"],
        "destroy_calls": state["destroy_calls"],
    }
    scenario_results.append({"input_keys": list(keys), "expected": expected, "actual": actual})

    output = capsys.readouterr().out
    assert actual == expected
    assert state["camera_index"] == 0
    assert state["window_name"] == "Take selfie with python"
    assert state["sleeps"] == [5]
    assert [frame for _name, frame in shown] == [
        f"frame-{index}" for index in range(expected["read_calls"])
    ]
    assert output.count("Selfie taken!") == len(expected["saved_files"])
    assert ("Escape hit, closing the window" in output) == (
        ESCAPE in [key % 256 for key in keys[: expected["read_calls"]]]
    )


def test_failed_camera_read_stops_and_releases_resources(
    monkeypatch, capsys, scenario_results
):
    fake_cv2, saved, shown, state = make_cv2([SPACE, SPACE], fail_read_at=1)
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)

    runpy.run_path(str(SCRIPT))

    output = capsys.readouterr().out
    expected = {
        "saved_files": ["Selfie_0.jpg"],
        "read_calls": 2,
        "release_calls": 1,
        "destroy_calls": 1,
    }
    actual = {
        "saved_files": [filename for filename, _frame in saved],
        "read_calls": state["read_calls"],
        "release_calls": state["release_calls"],
        "destroy_calls": state["destroy_calls"],
    }
    scenario_results.append(
        {
            "input_keys": [SPACE, SPACE],
            "camera_read_fails_at": 1,
            "expected": expected,
            "actual": actual,
        }
    )
    assert actual == expected
    assert [frame for _name, frame in shown] == ["frame-0"]
    assert "Failed to grab frame" in output
