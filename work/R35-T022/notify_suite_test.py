import json
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch


RESULTS_FILE = Path(__file__).with_name("check_results.json")
MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "Run Then Notify"
    / "run_then_notify.py"
)
MODULE_SPEC = importlib.util.spec_from_file_location(
    "run_then_notify_under_test", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
run_then_notify = importlib.util.module_from_spec(MODULE_SPEC)
with patch("builtins.input", return_value="sender@example.com"), patch(
    "getpass.getpass", return_value="test-password"
):
    MODULE_SPEC.loader.exec_module(run_then_notify)


def record_check(
    name: str,
    inputs: dict[str, object],
    expected: dict[str, object],
    actual: dict[str, object],
) -> None:
    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    checks = results["checks"]
    passed = expected == actual
    checks.append(
        {
            "name": name,
            "inputs": inputs,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        }
    )
    RESULTS_FILE.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    assert passed, f"{name}: expected {expected!r}, got {actual!r}"


def send_with_mocked_smtp(arguments: dict[str, object]) -> tuple[object, Mock, Mock]:
    smtp = Mock()
    with patch.object(
        run_then_notify.smtplib, "SMTP", return_value=smtp
    ) as smtp_factory:
        result = run_then_notify.send_text_email(**arguments)
    return result, smtp, smtp_factory


def test_send_text_email_sends_smallest_nonempty_inputs() -> None:
    inputs: dict[str, object] = {
        "subject": "x",
        "message": "x",
        "recipient_email": "a@b.co",
        "sender_email": "a@b.co",
        "sender_password": "x",
        "smtp_server": "localhost",
        "smtp_port": 1,
    }
    result, smtp, smtp_factory = send_with_mocked_smtp(inputs)
    sent_message = smtp.sendmail.call_args.args[2]
    actual: dict[str, object] = {
        "return_value": result,
        "smtp_constructor": list(smtp_factory.call_args.args),
        "tls_started": smtp.starttls.call_count == 1,
        "login_arguments": list(smtp.login.call_args.args),
        "mail_arguments": list(smtp.sendmail.call_args.args[:2]),
        "subject_in_message": "Subject: x" in sent_message,
        "recipient_in_message": "To: a@b.co" in sent_message,
        "body_in_message": "x" in sent_message,
        "quit_called": smtp.quit.call_count == 1,
    }
    expected: dict[str, object] = {
        "return_value": None,
        "smtp_constructor": ["localhost", 1],
        "tls_started": True,
        "login_arguments": ["a@b.co", "x"],
        "mail_arguments": ["a@b.co", "a@b.co"],
        "subject_in_message": True,
        "recipient_in_message": True,
        "body_in_message": True,
        "quit_called": True,
    }
    record_check("smallest_nonempty_inputs", inputs, expected, actual)


def test_send_text_email_sends_ordinary_inputs() -> None:
    inputs: dict[str, object] = {
        "subject": "Build status",
        "message": "Build completed",
        "recipient_email": "recipient@example.com",
        "sender_email": "sender@example.com",
        "sender_password": "test-password",
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
    }
    result, smtp, smtp_factory = send_with_mocked_smtp(inputs)
    sent_message = smtp.sendmail.call_args.args[2]
    actual: dict[str, object] = {
        "return_value": result,
        "smtp_constructor": list(smtp_factory.call_args.args),
        "tls_started": smtp.starttls.call_count == 1,
        "login_arguments": list(smtp.login.call_args.args),
        "mail_arguments": list(smtp.sendmail.call_args.args[:2]),
        "subject_in_message": "Subject: Build status" in sent_message,
        "recipient_in_message": "To: recipient@example.com" in sent_message,
        "body_in_message": "Build completed" in sent_message,
        "quit_called": smtp.quit.call_count == 1,
    }
    expected: dict[str, object] = {
        "return_value": None,
        "smtp_constructor": ["smtp.example.com", 587],
        "tls_started": True,
        "login_arguments": ["sender@example.com", "test-password"],
        "mail_arguments": ["sender@example.com", "recipient@example.com"],
        "subject_in_message": True,
        "recipient_in_message": True,
        "body_in_message": True,
        "quit_called": True,
    }
    record_check("ordinary_inputs", inputs, expected, actual)


def test_send_text_email_reports_smtp_failure() -> None:
    inputs: dict[str, object] = {
        "subject": "Build status",
        "message": "Build completed",
        "recipient_email": "recipient@example.com",
        "sender_email": "sender@example.com",
        "sender_password": "test-password",
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
    }
    smtp = Mock()
    smtp.starttls.side_effect = OSError("temporary SMTP failure")
    with patch.object(run_then_notify.smtplib, "SMTP", return_value=smtp):
        with patch("builtins.print") as print_mock:
            result = run_then_notify.send_text_email(**inputs)

    actual: dict[str, object] = {
        "return_value": result,
        "printed_error": list(print_mock.call_args.args),
        "quit_called": smtp.quit.call_count == 1,
    }
    expected: dict[str, object] = {
        "return_value": None,
        "printed_error": ["Email could not be sent: temporary SMTP failure"],
        "quit_called": False,
    }
    record_check("smtp_error_path", inputs, expected, actual)
