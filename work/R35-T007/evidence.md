# R35-T007 Evidence — Publish a runnable example for EmailSender

## Task
**R35-T007 · 7 of 10** — Publish a runnable example for EmailSender (Birthday-Manager.py) [Automating Emails]

## What was done
Added a concrete executable worked example to `EmailSender`'s docstring in `Automating Emails/Birthday-Manager.py`, showing the decisive state transition: how `send_email(recipient, message)` routes input through the intermediate state (`sent` list) to the final result (SMTP call or recorded stub).

External I/O (SMTP/SSL) is replaced by `StubEmailSender` so the example runs without live credentials in any environment.

## Precondition anchors
```python
class EmailSender(ABC):   # line 7 — precondition: ABC importable
updated_lines = []        # remove_birthday data anchor
```

## Fixture

| Input | Value |
|-------|-------|
| Smallest valid input | `recipient=""`, `message=""` → `sent == [('', '')]` |
| Ordinary input | `recipient="alice@example.com"`, `message=BirthdayMessage.create_message("Alice")` |

Independently calculated expected outputs (written before editing):
- `send_email("", "")` → `sent == [("", "")]`, returns `None`
- `send_email("alice@example.com", msg)` → `sent[-1][0] == "alice@example.com"`, `"Happy Birthday" in sent[-1][1]`
- Intermediate state: `len(sent)` grows by 1 per call

## Tests
File: `Automating Emails/test_birthday_manager.py`

| Test | Description |
|------|-------------|
| `test_send_email_smallest_records_call` | send_email("","") → sent==[("","")] |
| `test_send_email_smallest_returns_none` | returns None for smallest input |
| `test_intermediate_state_smallest` | sent grows from 0→1 |
| `test_send_email_ordinary_records_recipient` | recipient recorded correctly |
| `test_send_email_ordinary_message_contains_name` | "Alice" in message |
| `test_send_email_ordinary_message_contains_birthday_wish` | "Happy Birthday" in message |
| `test_send_email_ordinary_returns_none` | returns None for ordinary input |
| `test_create_message_smallest` | create_message("") starts with "Hi ," |
| `test_create_message_ordinary` | create_message("Alice") == expected string |
| `test_docstring_example_smallest` | docstring example smallest executes correctly |
| `test_docstring_example_ordinary` | docstring example ordinary executes correctly |
| `test_docstring_example_intermediate_state` | sent grows to 2 after 2 calls |

## Check run

```
python3 work/R35-T007/check.py
```

**Result: 12/12 passed — PASS**
**FORCE_WRONG=1: EXIT_CODE=1 (failure detected correctly)**

## Tool versions
- Python: 3.15.0
- pytest: 9.2.0
- smtplib/ssl: mocked — no live credentials needed
