"""Tests for OTP Verify/Otpverification.py
==========================================

Each test names the source line that establishes its precondition.

Fixture
-------
``fixed_rng`` — a seeded ``random.Random(42)`` instance so all property
tests are deterministic and reproducible (seed = 42).

Invariants under test
---------------------
1. generate_otp always returns a str of length exactly 6             (src L8; current L71)
2. every character of generate_otp output is in '0123456789'        (src L9; current L72)
3. verify_otp returns True iff inputs are equal strings              (src L18; current L82)
4. verify_otp returns False for any mismatch (including near-misses) (src L18; current L82)
5. send_otp_email formats message as "<otp> is your OTP"            (src L10; current L91)
6. run_interactive prints "Verified" on match                        (src L19; current L114)
7. run_interactive prints "Please Check your OTP again" on mismatch  (src L21; current L116)
8. Property: 100 bounded valid OTPs all satisfy len==6 and digit-only (src L8-9; current L71-72)

Current line numbers refer to Otpverification.py; ``src Lx`` denotes the
corresponding line in the original, unmodularized script.
"""

import random
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, call

# ---------------------------------------------------------------------------
# Path setup — import the module under test without installing anything
# ---------------------------------------------------------------------------
_OTP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _OTP_DIR not in sys.path:
    sys.path.insert(0, _OTP_DIR)

import Otpverification as otp_mod   # noqa: E402  (must come after path setup)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXED_SEED = 42
PROPERTY_CASES = 100   # generate at least 100 bounded valid cases
ORDINARY_INPUT = {"seed": 42}
ORDINARY_EXPECTED_OTP = "602276"  # manually mapped from the first six seed-42 samples


def _make_rng():
    """Return a freshly seeded Random so tests are independent."""
    return random.Random(FIXED_SEED)


# ---------------------------------------------------------------------------
# Unit tests — smallest valid input
# ---------------------------------------------------------------------------

class TestGenerateOtpSmallestInput(unittest.TestCase):
    """Smallest valid input: generate_otp with a seeded RNG whose .random()
    always returns 0.0  → every digit is '0' → OTP is '000000'.

    Precondition (src L8): loop runs 6 times.
    Precondition (src L9): digit = DIGITS[floor(random()*10)].
    """

    def setUp(self):
        # Deterministic RNG: random() always yields 0.0
        self.zero_rng = MagicMock()
        self.zero_rng.random.return_value = 0.0  # floor(0.0*10)=0 → '0'

    def test_length_is_six_smallest(self):
        """src L8: loop range(6) produces exactly 6 characters."""
        result = otp_mod.generate_otp(rng=self.zero_rng)
        self.assertEqual(len(result), 6,
                         msg=f"Expected length 6, got {len(result)!r}")

    def test_all_zeros_smallest(self):
        """src L9: when rng.random()==0.0, every digit maps to '0'."""
        result = otp_mod.generate_otp(rng=self.zero_rng)
        # Independently calculated expected output: '000000'
        self.assertEqual(result, "000000",
                         msg=f"Expected '000000', got {result!r}")

    def test_rng_called_six_times(self):
        """src L8: random() is called once per loop iteration (6 times)."""
        otp_mod.generate_otp(rng=self.zero_rng)
        self.assertEqual(self.zero_rng.random.call_count, 6)


# ---------------------------------------------------------------------------
# Unit tests — ordinary input
# ---------------------------------------------------------------------------

class TestGenerateOtpOrdinaryInput(unittest.TestCase):
    """Ordinary input: generate_otp with seed=42.

    With random.Random(42), the first 6 calls to .random() produce:
      0.6394267984578837  → digit 6
      0.025010755222666936 → digit 0
      0.27502931836911926  → digit 2
      0.22321073814882275  → digit 2
      0.7364712141640124   → digit 7
      0.6766994874229113   → digit 6
    Literal input: seed=42. Independently calculated expected OTP: '602276'.
    """

    def setUp(self):
        self.rng = _make_rng()
        # Literal oracle: the six seed-42 samples map to digits 6, 0, 2, 2, 7, 6.
        self._expected = ORDINARY_EXPECTED_OTP

    def test_length_is_six_ordinary(self):
        """src L8: output is always 6 characters for ordinary seed=42 input."""
        result = otp_mod.generate_otp(rng=_make_rng())
        self.assertEqual(len(result), 6)

    def test_deterministic_output_seed42(self):
        """src L9: seed=42 produces same OTP every time (determinism check)."""
        # Literal input and independently calculated expected result.
        result = otp_mod.generate_otp(rng=random.Random(ORDINARY_INPUT["seed"]))
        self.assertEqual(result, self._expected,
                         msg=f"Expected {self._expected!r}, got {result!r}")

    def test_only_digits_ordinary(self):
        """src L9: every character of the OTP is an ASCII digit."""
        result = otp_mod.generate_otp(rng=_make_rng())
        for idx, ch in enumerate(result):
            self.assertIn(ch, "0123456789",
                          msg=f"Non-digit {ch!r} at position {idx}")


# ---------------------------------------------------------------------------
# Unit tests — verify_otp
# ---------------------------------------------------------------------------

class TestVerifyOtpSmallest(unittest.TestCase):
    """Smallest valid input: single-character digit strings.

    src L18: comparison is ``a == OTP`` (exact string equality).
    """

    def test_match_smallest(self):
        """src L18: '0' == '0' → True."""
        # Literal input / independently calculated expected output
        self.assertTrue(otp_mod.verify_otp("0", "0"))

    def test_mismatch_smallest(self):
        """src L18: '0' == '1' → False."""
        self.assertFalse(otp_mod.verify_otp("0", "1"))


class TestVerifyOtpOrdinary(unittest.TestCase):
    """Ordinary 6-digit inputs.

    src L18: exact string equality, no coercion.
    """

    def test_match_six_digits(self):
        """src L18: '123456' == '123456' → True."""
        # Literal input and independently calculated expected output
        self.assertTrue(otp_mod.verify_otp("123456", "123456"))

    def test_mismatch_last_digit(self):
        """src L18: near-miss '123457' != '123456' → False."""
        self.assertFalse(otp_mod.verify_otp("123457", "123456"))

    def test_mismatch_leading_zero(self):
        """src L18: '023456' != '123456' → False (no int coercion)."""
        self.assertFalse(otp_mod.verify_otp("023456", "123456"))

    def test_mismatch_extra_space(self):
        """src L18: ' 123456' != '123456' → False (no stripping)."""
        self.assertFalse(otp_mod.verify_otp(" 123456", "123456"))

    def test_case_sensitivity(self):
        """src L18: equality is case-sensitive (edge case with alpha chars)."""
        self.assertFalse(otp_mod.verify_otp("ABCDEF", "abcdef"))

    def test_empty_vs_empty(self):
        """src L18: '' == '' → True (boundary: both empty strings)."""
        self.assertTrue(otp_mod.verify_otp("", ""))

    def test_empty_vs_nonempty(self):
        """src L18: '' != '123456' → False."""
        self.assertFalse(otp_mod.verify_otp("", "123456"))


# ---------------------------------------------------------------------------
# Unit tests — send_otp_email
# ---------------------------------------------------------------------------

class TestSendOtpEmail(unittest.TestCase):
    """Tests for send_otp_email message formatting.

    src L10: msg = otp + ' is your OTP'
    src L16: smtp_client.sendmail(sender, recipient, msg)
    """

    def setUp(self):
        self.smtp = MagicMock()

    def test_message_format(self):
        """src L10: message is '<OTP> is your OTP'."""
        otp_mod.send_otp_email(self.smtp, "s@g.com", "r@g.com", "123456")
        self.smtp.sendmail.assert_called_once_with(
            "s@g.com", "r@g.com", "123456 is your OTP"
        )

    def test_message_format_all_zeros(self):
        """src L10: OTP='000000' → '000000 is your OTP'."""
        otp_mod.send_otp_email(self.smtp, "s@g.com", "r@g.com", "000000")
        self.smtp.sendmail.assert_called_once_with(
            "s@g.com", "r@g.com", "000000 is your OTP"
        )


# ---------------------------------------------------------------------------
# Unit tests — run_interactive (mocking all I/O)
# ---------------------------------------------------------------------------

class TestRunInteractiveVerified(unittest.TestCase):
    """Precondition (src L18): if user enters matching OTP, prints Verified."""

    def test_verified_path(self):
        """src L19: 'Verified' is printed when user_input == otp."""
        printed = []

        # We need to control the generated OTP → patch generate_otp
        with patch.object(otp_mod, "generate_otp", return_value="654321"):
            inputs_iter = iter(["user@test.com", "654321"])
            result = otp_mod.run_interactive(
                smtp_factory=None,
                input_fn=lambda _prompt="": next(inputs_iter),
                print_fn=printed.append,
            )

        self.assertTrue(result, "run_interactive should return True on match")
        self.assertIn("Verified", printed,
                      msg=f"Expected 'Verified' in output, got {printed!r}")

    def test_not_verified_path(self):
        """src L21: 'Please Check your OTP again' when user_input != otp."""
        printed = []

        with patch.object(otp_mod, "generate_otp", return_value="654321"):
            inputs_iter = iter(["user@test.com", "000000"])
            result = otp_mod.run_interactive(
                smtp_factory=None,
                input_fn=lambda _prompt="": next(inputs_iter),
                print_fn=printed.append,
            )

        self.assertFalse(result)
        self.assertIn("Please Check your OTP again", printed,
                      msg=f"Expected failure message, got {printed!r}")


# ---------------------------------------------------------------------------
# Property-based test: 100 bounded valid cases, fixed seed
# ---------------------------------------------------------------------------

class TestGenerateOtpProperty(unittest.TestCase):
    """Generate PROPERTY_CASES (>=100) OTPs with a fixed seed and verify
    all satisfy the structural invariants (src L8, src L9).

    A readable small case is preserved as a named constant for review.
    """

    # Readable small case (seed=42, first OTP in sequence)
    READABLE_CASE = {
        "seed": FIXED_SEED,
        "case_index": 0,
        "description": "First OTP from seed=42 Random state",
    }

    def test_one_hundred_valid_cases(self):
        """src L8-9: all 100 OTPs from seed=42 have length==6, digits only."""
        rng = random.Random(FIXED_SEED)
        failures = []

        for i in range(PROPERTY_CASES):
            otp = otp_mod.generate_otp(rng=rng)
            if len(otp) != 6:
                failures.append(f"case {i}: len={len(otp)} for otp={otp!r}")
            for ch in otp:
                if ch not in "0123456789":
                    failures.append(f"case {i}: non-digit {ch!r} in {otp!r}")

        self.assertEqual(
            failures, [],
            msg=f"{len(failures)} failures:\n" + "\n".join(failures[:10])
        )

    def test_readable_small_case_determinism(self):
        """The readable small case (seed=42, index=0) is always reproducible."""
        rng = random.Random(FIXED_SEED)
        # Advance state to index 0 (no advancement needed for first case)
        otp = otp_mod.generate_otp(rng=rng)
        # Independently calculated literal for the readable seed-42 case.
        self.assertEqual(otp, ORDINARY_EXPECTED_OTP,
                 msg=f"Readable small case mismatch: {otp!r} != {ORDINARY_EXPECTED_OTP!r}")

    def test_all_one_hundred_are_strings(self):
        """src L8: generate_otp always returns a str (not int or None)."""
        rng = random.Random(FIXED_SEED)
        for i in range(PROPERTY_CASES):
            otp = otp_mod.generate_otp(rng=rng)
            self.assertIsInstance(otp, str,
                                  msg=f"case {i}: expected str, got {type(otp)}")

    def test_verify_roundtrip_all_hundred(self):
        """src L18: verify_otp(otp, otp) is True for every generated OTP."""
        rng = random.Random(FIXED_SEED)
        for i in range(PROPERTY_CASES):
            otp = otp_mod.generate_otp(rng=rng)
            self.assertTrue(
                otp_mod.verify_otp(otp, otp),
                msg=f"case {i}: roundtrip verify failed for otp={otp!r}"
            )

    def test_verify_cross_otps_false(self):
        """src L18: verify_otp(otp_a, otp_b) is False when otps differ."""
        rng = random.Random(FIXED_SEED)
        otps = [otp_mod.generate_otp(rng=rng) for _ in range(PROPERTY_CASES)]
        failures = []
        for i in range(PROPERTY_CASES - 1):
            if otps[i] != otps[i + 1]:  # skip rare collisions
                if otp_mod.verify_otp(otps[i], otps[i + 1]):
                    failures.append(
                        f"case {i}: verify_otp({otps[i]!r}, {otps[i+1]!r}) "
                        f"unexpectedly True"
                    )
        self.assertEqual(failures, [], msg="\n".join(failures[:5]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
