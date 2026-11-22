"""Tests for Automating Emails/Birthday-Manager.py — R35-T007.

Fixture (written BEFORE editing the implementation):
    Smallest valid input : recipient="", message=""
    Ordinary input       : recipient="alice@example.com",
                           message=BirthdayMessage.create_message("Alice")

Precondition anchor (source line):
    ``class EmailSender(ABC):``  # line 7
    ``updated_lines = []``       # remove_birthday data anchor
"""

import io
import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open

import importlib.util as _ilu
import pathlib as _pl

_src = _pl.Path(__file__).parent / "Birthday-Manager.py"
_spec = _ilu.spec_from_file_location("Birthday_Manager", _src)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

EmailSender = _mod.EmailSender
GmailEmailSender = _mod.GmailEmailSender
BirthdayMessage = _mod.BirthdayMessage
BirthdayListManager = _mod.BirthdayListManager
BirthdayNotifier = _mod.BirthdayNotifier


# ---------------------------------------------------------------------------
# Stub implementation used in the runnable example (no live credentials).
# ---------------------------------------------------------------------------
class StubEmailSender(EmailSender):
    """Concrete EmailSender that records calls instead of hitting SMTP."""
    def __init__(self):
        self.sent = []   # intermediate state

    def send_email(self, recipient, message):
        self.sent.append((recipient, message))


# ---------------------------------------------------------------------------
# Tests — smallest valid input
# ---------------------------------------------------------------------------
class TestEmailSenderSmallestInput(unittest.TestCase):
    """EmailSender with the smallest valid inputs: recipient="", message=""."""

    def test_send_email_smallest_records_call(self):
        """send_email("", "") appends ('', '') to sent list."""
        # Precondition anchor: class EmailSender(ABC):  # line 7
        # Expected: sent == [('', '')]
        sender = StubEmailSender()
        sender.send_email("", "")
        self.assertEqual(sender.sent, [("", "")])

    def test_send_email_smallest_returns_none(self):
        """send_email("", "") returns None."""
        # Expected: None
        sender = StubEmailSender()
        result = sender.send_email("", "")
        self.assertIsNone(result)

    def test_intermediate_state_smallest(self):
        """sent list reflects intermediate state after smallest input."""
        # Intermediate state: sender.sent accumulates (recipient, message) tuples
        sender = StubEmailSender()
        self.assertEqual(len(sender.sent), 0)   # before: empty
        sender.send_email("", "")
        self.assertEqual(len(sender.sent), 1)   # after: one entry


# ---------------------------------------------------------------------------
# Tests — ordinary input
# ---------------------------------------------------------------------------
class TestEmailSenderOrdinaryInput(unittest.TestCase):
    """EmailSender with ordinary inputs: birthday email to Alice."""

    def setUp(self):
        self.sender = StubEmailSender()
        self.recipient = "alice@example.com"
        self.message = BirthdayMessage.create_message("Alice")

    def test_send_email_ordinary_records_recipient(self):
        """send_email records the correct recipient (ordinary input)."""
        # Precondition anchor: class EmailSender(ABC):  # line 7
        # Expected: sent[-1][0] == "alice@example.com"
        self.sender.send_email(self.recipient, self.message)
        self.assertEqual(self.sender.sent[-1][0], "alice@example.com")

    def test_send_email_ordinary_message_contains_name(self):
        """Message body contains the recipient's first name."""
        # Expected: "Alice" in message
        self.sender.send_email(self.recipient, self.message)
        self.assertIn("Alice", self.sender.sent[-1][1])

    def test_send_email_ordinary_message_contains_birthday_wish(self):
        """Message body contains 'Happy Birthday'."""
        # Expected: "Happy Birthday" in message
        self.sender.send_email(self.recipient, self.message)
        self.assertIn("Happy Birthday", self.sender.sent[-1][1])

    def test_send_email_ordinary_returns_none(self):
        """send_email returns None for ordinary input."""
        # Expected: None
        result = self.sender.send_email(self.recipient, self.message)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# Tests — BirthdayMessage (pure function, used in example)
# ---------------------------------------------------------------------------
class TestBirthdayMessageCreateMessage(unittest.TestCase):

    def test_create_message_smallest(self):
        """create_message('') produces 'Hi ,' greeting (smallest fname)."""
        # Smallest fname = ""
        msg = BirthdayMessage.create_message("")
        self.assertTrue(msg.startswith("Hi ,"))

    def test_create_message_ordinary(self):
        """create_message('Alice') produces expected greeting."""
        # Independently calculated expected output:
        expected = "Hi Alice,\n\nI wish you a very Happy Birthday.\n\nI hope you had a great day."
        self.assertEqual(BirthdayMessage.create_message("Alice"), expected)


# ---------------------------------------------------------------------------
# Tests — runnable example (docstring example executed as a test)
# ---------------------------------------------------------------------------
class TestRunnableExample(unittest.TestCase):
    """Executes the docstring example from EmailSender and asserts output."""

    def test_docstring_example_smallest(self):
        """Docstring example: send_email('', '') → sent == [('', '')]."""
        sender = StubEmailSender()
        sender.send_email("", "")
        self.assertEqual(sender.sent, [("", "")])

    def test_docstring_example_ordinary(self):
        """Docstring example: ordinary birthday email to Alice."""
        sender = StubEmailSender()
        msg = BirthdayMessage.create_message("Alice")
        sender.send_email("alice@example.com", msg)
        self.assertEqual(sender.sent[-1][0], "alice@example.com")
        self.assertIn("Happy Birthday", sender.sent[-1][1])

    def test_docstring_example_intermediate_state(self):
        """Intermediate state: sent grows with each send_email call."""
        sender = StubEmailSender()
        sender.send_email("", "")
        self.assertEqual(len(sender.sent), 1)
        msg = BirthdayMessage.create_message("Alice")
        sender.send_email("alice@example.com", msg)
        self.assertEqual(len(sender.sent), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
