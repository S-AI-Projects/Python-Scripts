"""
Independent reference cross-check tests for send_email in Automate Emails Daily/main.py.

Preconditions and source anchors:
- Anchor 1: receiver_emails = ["receiver1-email@gmail.com", "receiver2-email@gmail.com"] (main.py)
- Anchor 2: attachments = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"] (main.py)
- send_email near line 8
"""

import email
import io
import os
import sys
import unittest
from email.utils import formataddr
from unittest.mock import MagicMock, mock_open, patch

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import main


def email_oracle(sender_email, sender_name, password, receiver_emails, email_body,
                 email_subject="No subject", is_html=False, attachments=None):
    """
    Independent reference oracle for send_email.
    Computes expected headers, recipient delivery sequence, and dispatch count
    without invoking the implementation under test.
    """
    expected_from = formataddr((f"{sender_name}", f"{sender_email}"))
    expected_bcc = sender_email
    expected_subject = email_subject
    expected_receivers = list(receiver_emails)
    expected_sendmail_calls = [
        (sender_email, receiver) for receiver in receiver_emails
    ]
    return {
        "expected_from": expected_from,
        "expected_bcc": expected_bcc,
        "expected_subject": expected_subject,
        "expected_receivers": expected_receivers,
        "expected_sendmail_calls": expected_sendmail_calls,
        "call_count": len(receiver_emails),
        "return_value": None,
    }


class TestSendEmailCrossCheck(unittest.TestCase):
    """Cross-check test suite comparing send_email against the independent reference oracle."""

    def setUp(self):
        self.mock_smtp = MagicMock()
        self.smtp_patcher = patch("smtplib.SMTP", return_value=self.mock_smtp)
        self.mock_smtp_class = self.smtp_patcher.start()

    def tearDown(self):
        self.smtp_patcher.stop()

    def test_precondition_anchors(self):
        """Verify baseline data anchors exist in main.py."""
        source_path = os.path.join(MODULE_DIR, "main.py")
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('receiver_emails = ["receiver1-email@gmail.com", "receiver2-email@gmail.com"]', content)
        self.assertIn('attachments = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"]', content)
        self.assertIn("def send_email(", content)

    def test_smallest_valid_input_cross_check(self):
        """
        Cross-check smallest valid input: single recipient, plain text, no attachments.
        Precondition: main.py line 8 send_email definition.
        """
        sender = "user@gmail.com"
        name = "User"
        pwd = "pwd"
        receivers = ["receiver1-email@gmail.com"]
        body = "Hi"
        subject = "No subject"

        oracle_out = email_oracle(sender, name, pwd, receivers, body, email_subject=subject)

        with patch("sys.stdout", io.StringIO()):
            res = main.send_email(sender, name, pwd, receivers, body, email_subject=subject)

        self.assertEqual(res, oracle_out["return_value"])
        self.assertEqual(self.mock_smtp.sendmail.call_count, oracle_out["call_count"])

        # Check delivered recipient call
        args = self.mock_smtp.sendmail.call_args_list[0][0]
        self.assertEqual(args[0], sender)
        self.assertEqual(args[1], receivers[0])

        # Verify parsed message headers against oracle
        parsed_msg = email.message_from_string(args[2])
        self.assertEqual(parsed_msg["From"], oracle_out["expected_from"])
        self.assertEqual(parsed_msg["Subject"], oracle_out["expected_subject"])
        self.assertEqual(parsed_msg["BCC"], oracle_out["expected_bcc"])
        self.assertEqual(parsed_msg["To"], receivers[0])

    def test_ordinary_valid_input_cross_check(self):
        """
        Cross-check ordinary input from source fixture:
        2 receivers, HTML body, 2 attachments.
        """
        sender = "your-email@gmail.com"
        name = "your name"
        pwd = "secret"
        receivers = ["receiver1-email@gmail.com", "receiver2-email@gmail.com"]
        body = "<h1>Good Morning!</h1><p>Hope you have a <strong>wonderful day</strong>.</p>"
        subject = "Good morning"
        attachs = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"]

        oracle_out = email_oracle(sender, name, pwd, receivers, body, email_subject=subject, is_html=True, attachments=attachs)

        fake_file = mock_open(read_data=b"%PDF-1.4 dummy content")
        with patch("builtins.open", fake_file), patch("sys.stdout", io.StringIO()):
            res = main.send_email(sender, name, pwd, receivers, body, email_subject=subject, is_html=True, attachments=attachs)

        self.assertEqual(res, oracle_out["return_value"])
        self.assertEqual(self.mock_smtp.sendmail.call_count, oracle_out["call_count"])

        for idx, receiver in enumerate(receivers):
            args = self.mock_smtp.sendmail.call_args_list[idx][0]
            self.assertEqual(args[0], sender)
            self.assertEqual(args[1], receiver)
            parsed_msg = email.message_from_string(args[2])
            self.assertEqual(parsed_msg["From"], oracle_out["expected_from"])
            self.assertEqual(parsed_msg["Subject"], oracle_out["expected_subject"])
            self.assertEqual(parsed_msg["To"], receiver)

    def test_20_varied_inputs_cross_check(self):
        """
        Enumerate at least 20 small valid inputs across the domain and compare
        against the independent oracle.
        """
        test_matrix = [
            # sender_name, subject, is_html, receivers_count, attachments_count
            ("Alice", "Meeting Notice", False, 1, 0),
            ("Bob", "Project Update", True, 2, 0),
            ("Charlie", "Invoice #101", False, 1, 1),
            ("Diana", "Weekly Summary", True, 3, 1),
            ("Ethan", "Welcome!", False, 2, 2),
            ("Fiona", "Daily Standup", True, 1, 0),
            ("George", "Alert: Disk usage", False, 3, 0),
            ("Hannah", "Newsletter Issue 42", True, 2, 1),
            ("Ian", "Quick Question", False, 1, 0),
            ("Julia", "Monthly Report", True, 4, 2),
            ("Kevin", "Bug Report", False, 1, 1),
            ("Laura", "Event Invitation", True, 2, 0),
            ("Michael", "Receipt confirmation", False, 1, 0),
            ("Nina", "Check-in", True, 3, 1),
            ("Oscar", "Release notes v2.0", False, 2, 0),
            ("Paula", "Contract draft", True, 1, 2),
            ("Quinn", "Schedule reminder", False, 1, 0),
            ("Rachel", "Announcement", True, 2, 1),
            ("Sam", "Thank you", False, 1, 0),
            ("Tina", "Final Reminder", True, 3, 0),
            ("Victor", "System Backup Status", False, 2, 1),
        ]
        self.assertGreaterEqual(len(test_matrix), 20)

        fake_file = mock_open(read_data=b"dummy attachment data")
        for i, (name, subj, html_flag, r_count, a_count) in enumerate(test_matrix, start=1):
            self.mock_smtp.reset_mock()
            sender = f"{name.lower()}@example.com"
            pwd = "password123"
            receivers = [f"rec{k}@domain.org" for k in range(r_count)]
            body = f"<p>Hello from test case {i}</p>" if html_flag else f"Hello from test case {i}"
            attachs = [f"doc_{k}.pdf" for k in range(a_count)] if a_count > 0 else None

            oracle_out = email_oracle(
                sender, name, pwd, receivers, body,
                email_subject=subj, is_html=html_flag, attachments=attachs
            )

            with patch("builtins.open", fake_file), patch("sys.stdout", io.StringIO()):
                res = main.send_email(
                    sender, name, pwd, receivers, body,
                    email_subject=subj, is_html=html_flag, attachments=attachs
                )

            # Assert return value matches oracle (None)
            self.assertEqual(res, oracle_out["return_value"], f"Case {i}: return value mismatch")
            # Assert sendmail invocation count matches oracle
            self.assertEqual(self.mock_smtp.sendmail.call_count, oracle_out["call_count"], f"Case {i}: call count mismatch")

            # Assert each call matches oracle
            for idx, receiver in enumerate(receivers):
                args = self.mock_smtp.sendmail.call_args_list[idx][0]
                self.assertEqual(args[0], sender, f"Case {i}: sender mismatch")
                self.assertEqual(args[1], receiver, f"Case {i}: recipient mismatch")
                parsed_msg = email.message_from_string(args[2])
                self.assertEqual(parsed_msg["From"], oracle_out["expected_from"], f"Case {i}: From header mismatch")
                self.assertEqual(parsed_msg["Subject"], oracle_out["expected_subject"], f"Case {i}: Subject header mismatch")
                self.assertEqual(parsed_msg["BCC"], oracle_out["expected_bcc"], f"Case {i}: BCC header mismatch")
                self.assertEqual(parsed_msg["To"], receiver, f"Case {i}: To header mismatch")

    def test_input_non_mutation(self):
        """Assert receiver_emails and attachments lists are not mutated in-place."""
        receivers = ["receiver1-email@gmail.com", "receiver2-email@gmail.com"]
        attachs = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"]
        orig_receivers = list(receivers)
        orig_attachs = list(attachs)

        fake_file = mock_open(read_data=b"test data")
        with patch("builtins.open", fake_file), patch("sys.stdout", io.StringIO()):
            main.send_email("user@gmail.com", "User", "pwd", receivers, "Body", attachments=attachs)

        self.assertEqual(receivers, orig_receivers, "receiver_emails was mutated")
        self.assertEqual(attachs, orig_attachs, "attachments was mutated")


if __name__ == "__main__":
    unittest.main()
