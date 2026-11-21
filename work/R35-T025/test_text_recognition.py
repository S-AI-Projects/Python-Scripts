import importlib.util
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Text Recognition" / "text_recognition.py"
WORK_DIR = Path(__file__).resolve().parent
FIXTURE_A = "https://images.example/fixture-a.png"
FIXTURE_B = "https://images.example/fixture-b.png"


def load_recognition_module():
    spec = importlib.util.spec_from_file_location(
        "text_recognition_under_test", MODULE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_external_mocks(monkeypatch, events, request_error=None):
    requests_module = types.ModuleType("requests")

    def get(url, stream):
        events.append(("requests.get", url, stream))
        if request_error is not None:
            raise request_error
        return SimpleNamespace(raw=url)

    requests_module.get = get

    class FakeImage:
        def __init__(self, source):
            self.source = source

        def convert(self, mode):
            events.append(("image.convert", mode, self.source))
            return self

    image_api = SimpleNamespace(
        open=lambda source: (
            events.append(("image.open", source)) or FakeImage(source)
        )
    )
    pil_module = types.ModuleType("PIL")
    pil_module.Image = image_api

    class FakeProcessor:
        @classmethod
        def from_pretrained(cls, model_id):
            events.append(("processor.load", model_id))
            return cls()

        def __call__(self, images, return_tensors):
            events.append(("processor.call", images.source, return_tensors))
            return SimpleNamespace(pixel_values=images.source)

        def batch_decode(self, generated_ids, skip_special_tokens):
            events.append(("processor.decode", generated_ids, skip_special_tokens))
            return [f"recognized:{generated_ids[0]}"]

    class FakeModel:
        @classmethod
        def from_pretrained(cls, model_id):
            events.append(("model.load", model_id))
            return cls()

        def generate(self, pixel_values):
            events.append(("model.generate", pixel_values))
            return [pixel_values]

    transformers_module = types.ModuleType("transformers")
    transformers_module.TrOCRProcessor = FakeProcessor
    transformers_module.VisionEncoderDecoderModel = FakeModel

    monkeypatch.setitem(sys.modules, "requests", requests_module)
    monkeypatch.setitem(sys.modules, "PIL", pil_module)
    monkeypatch.setitem(sys.modules, "transformers", transformers_module)


def expected_text(image_url):
    return f"recognized:{image_url}"


def test_fixture_is_repeatable_in_fresh_state_and_after_another_input(
    monkeypatch,
):
    cases = []

    for run_name in ("fresh-run-1", "fresh-run-2"):
        events = []
        install_external_mocks(monkeypatch, events)
        module = load_recognition_module()
        actual = module.recognize_text(FIXTURE_A)
        cases.append(
            {
                "scenario": run_name,
                "input_url": FIXTURE_A,
                "expected": expected_text(FIXTURE_A),
                "actual": actual,
            }
        )

    events = []
    install_external_mocks(monkeypatch, events)
    module = load_recognition_module()
    for run_name, image_url in (
        ("sequence-before-other-input", FIXTURE_A),
        ("other-valid-input", FIXTURE_B),
        ("sequence-after-other-input", FIXTURE_A),
    ):
        actual = module.recognize_text(image_url)
        cases.append(
            {
                "scenario": run_name,
                "input_url": image_url,
                "expected": expected_text(image_url),
                "actual": actual,
            }
        )

    evidence = {
        "external_io": "mocked: requests.get, PIL.Image.open, Transformers model",
        "cases": cases,
    }
    (WORK_DIR / "inputs_expected_actual.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    assert [case["actual"] for case in cases[:2]] == [
        expected_text(FIXTURE_A),
        expected_text(FIXTURE_A),
    ]
    assert cases[2]["actual"] == cases[4]["actual"] == expected_text(FIXTURE_A)
    assert cases[3]["actual"] == expected_text(FIXTURE_B)
    assert [event[0] for event in events].count("processor.load") == 3
    assert [event[0] for event in events].count("model.load") == 3


def test_recognizer_forwards_input_and_returns_decoded_text(monkeypatch):
    events = []
    install_external_mocks(monkeypatch, events)

    actual = load_recognition_module().recognize_text(FIXTURE_A)

    assert actual == expected_text(FIXTURE_A)
    assert events == [
        ("requests.get", FIXTURE_A, True),
        ("image.open", FIXTURE_A),
        ("image.convert", "RGB", FIXTURE_A),
        (
            "processor.load",
            "microsoft/trocr-large-handwritten",
        ),
        ("model.load", "microsoft/trocr-large-handwritten"),
        ("processor.call", FIXTURE_A, "pt"),
        ("model.generate", FIXTURE_A),
        ("processor.decode", [FIXTURE_A], True),
    ]


def test_request_failures_are_propagated(monkeypatch):
    events = []
    error = RuntimeError("image service unavailable")
    install_external_mocks(monkeypatch, events, request_error=error)

    try:
        load_recognition_module().recognize_text(FIXTURE_A)
    except RuntimeError as caught:
        assert caught is error
    else:
        raise AssertionError("request failure was not propagated")
