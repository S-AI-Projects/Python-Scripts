import json
import runpy
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "QR with Logo" / "qr.py"
WORK_DIR = Path(__file__).resolve().parent
LOGO_PATH = "github-logo.png"
TARGET_URL = "https://github.com/shashank-amireddy"


class FakeImage:
    def __init__(self, size, label, events):
        self.size = size
        self.label = label
        self.events = events

    def convert(self, mode):
        self.events.append(("convert", self.label, mode))
        return FakeImage(self.size, f"{self.label}:{mode}", self.events)

    def resize(self, size, resample):
        self.events.append(("resize", self.label, size, resample))
        return FakeImage(size, f"{self.label}:resized", self.events)

    def paste(self, image, position, mask):
        self.events.append(
            ("paste", self.label, image.label, position, mask.label, image is mask)
        )

    def save(self, path):
        self.events.append(("save", self.label, path))


def install_external_mocks(monkeypatch, events):
    image_module = types.ModuleType("PIL.Image")
    image_module.LANCZOS = "LANCZOS"

    def open_image(path):
        events.append(("open", path))
        return FakeImage((20, 10), "logo", events)

    image_module.open = open_image
    pil_module = types.ModuleType("PIL")
    pil_module.Image = image_module

    class FakeQRCode:
        def __init__(self, error_correction):
            events.append(("qr.init", error_correction))

        def add_data(self, data):
            events.append(("qr.add_data", data))

        def make(self):
            events.append(("qr.make",))

        def make_image(self, fill_color, back_color):
            events.append(("qr.make_image", fill_color, back_color))
            return FakeImage((200, 200), "qr", events)

    qrcode_module = types.ModuleType("qrcode")
    qrcode_module.constants = types.SimpleNamespace(ERROR_CORRECT_H="H")
    qrcode_module.QRCode = FakeQRCode

    monkeypatch.setitem(sys.modules, "PIL", pil_module)
    monkeypatch.setitem(sys.modules, "PIL.Image", image_module)
    monkeypatch.setitem(sys.modules, "qrcode", qrcode_module)


def test_script_generates_centered_qr_with_resized_logo(monkeypatch, capsys):
    events = []
    install_external_mocks(monkeypatch, events)
    runpy.run_path(str(SCRIPT))
    stdout = capsys.readouterr().out

    expected_events = [
        ("open", LOGO_PATH),
        ("convert", "logo", "RGBA"),
        ("resize", "logo:RGBA", (100, 50), "LANCZOS"),
        ("qr.init", "H"),
        ("qr.add_data", TARGET_URL),
        ("qr.make",),
        ("qr.make_image", "black", "white"),
        ("convert", "qr", "RGBA"),
        (
            "paste",
            "qr:RGBA",
            "logo:RGBA:resized",
            (50, 75),
            "logo:RGBA:resized",
            True,
        ),
        ("save", "qr:RGBA", "qr_with_logo.png"),
    ]
    evidence = {
        "inputs": {
            "logo_path": LOGO_PATH,
            "logo_size": [20, 10],
            "target_url": TARGET_URL,
            "qr_image_size": [200, 200],
        },
        "expected": {
            "events": expected_events,
            "stdout": "QR code generated!\n",
        },
        "actual": {
            "events": events,
            "stdout": stdout,
        },
    }
    (WORK_DIR / "inputs_expected_actual.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    assert events == expected_events
    assert stdout == "QR code generated!\n"


def test_resize_logo_preserves_aspect_ratio_and_image_type(monkeypatch, capsys):
    events = []
    install_external_mocks(monkeypatch, events)
    namespace = runpy.run_path(str(SCRIPT))
    capsys.readouterr()
    events.clear()
    logo = FakeImage((20, 10), "test-logo", events)

    resized = namespace["resize_logo"](logo)

    assert type(resized) is FakeImage
    assert resized.size == (100, 50)
    assert events == [
        ("resize", "test-logo", (100, 50), "LANCZOS"),
    ]
