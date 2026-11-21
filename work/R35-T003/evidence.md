# R35-T003 Evidence

## Student Details
- **Student Name**: Nitesh Kumar
- **URN**: e26b07f0629
- **Task ID**: R35-T003 (Issue #3)
- **Repository**: S-AI-Projects/Python-Scripts
- **Assigned working branch**: student/e26b07f0629/R35-T003

## Target Item
- **Module**: `Automate Emails Daily/main.py`
- **Target Function**: `send_email` near line 8
- **Source Fixture / Precondition Anchors**:
  - `receiver_emails = ["receiver1-email@gmail.com", "receiver2-email@gmail.com"]` (main.py)
  - `attachments = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"]` (main.py)
  - `def send_email(...)` near line 8

## Independent Reference Oracle Design
The independent reference model `email_oracle` computes the expected message headers (`From`, `Subject`, `BCC`, `To`), delivery calls, and recipient sequence directly from the input specifications without invoking the `send_email` implementation under test:
- `expected_from = formataddr((sender_name, sender_email))`
- `expected_bcc = sender_email`
- `expected_subject = email_subject`
- `expected_sendmail_calls = [(sender_email, receiver) for receiver in receiver_emails]`
- `return_value = None`

## Tool Versions
- **Python**: 3.15.0
- **Platform**: macOS (Darwin arm64)
- **Git Branch**: `student/e26b07f0629/R35-T003`

## Test Results and Evidence

### 1. Smallest Supported Input Cross-Check
- **Input Parameters**:
  - `sender_email`: `"user@gmail.com"`
  - `sender_name`: `"User"`
  - `password`: `"pwd"`
  - `receiver_emails`: `["receiver1-email@gmail.com"]`
  - `email_body`: `"Hi"`
  - `email_subject`: `"No subject"`
  - `is_html`: `False`
  - `attachments`: `None`
- **Oracle Prediction**:
  - `From`: `"User <user@gmail.com>"`
  - `Subject`: `"No subject"`
  - `BCC`: `"user@gmail.com"`
  - `Sendmail calls`: `[('user@gmail.com', 'receiver1-email@gmail.com')]`
  - `Return value`: `None`
- **Implementation Result**: Matched oracle identically across all headers, calls, and return value -> **PASS**.

### 2. Ordinary Valid Input Cross-Check (Source Fixture)
- **Input Parameters**:
  - `sender_email`: `"your-email@gmail.com"`
  - `sender_name`: `"your name"`
  - `password`: `os.environ.get("EMAIL_PASSWORD")`
  - `receiver_emails`: `["receiver1-email@gmail.com", "receiver2-email@gmail.com"]`
  - `email_body`: `"<h1>Good Morning!</h1><p>Hope you have a <strong>wonderful day</strong>.</p>"`
  - `email_subject`: `"Good morning"`
  - `is_html`: `True`
  - `attachments`: `["path/to/attachment1.pdf", "path/to/attachment2.jpg"]`
- **Oracle Prediction**:
  - `From`: `"your name <your-email@gmail.com>"`
  - `Subject`: `"Good morning"`
  - `BCC`: `"your-email@gmail.com"`
  - `Sendmail calls`: `[('your-email@gmail.com', 'receiver1-email@gmail.com'), ('your-email@gmail.com', 'receiver2-email@gmail.com')]`
  - `Return value`: `None`
- **Implementation Result**: Matched oracle identically across all headers, calls, and return value -> **PASS**.

### 3. Enumerated Cross-Check Matrix (21 Valid Domain Configurations)
All 21 test configurations enumerated across variable recipient counts, plain text vs HTML, attachment configurations, and custom subjects matched the independent oracle with zero deviations:

| Case | Sender Name | Subject | HTML? | Receivers | Attachments | Oracle Match |
|---|---|---|---|---|---|---|
| 1 | Alice | Meeting Notice | False | 1 | 0 | **PASS** |
| 2 | Bob | Project Update | True | 2 | 0 | **PASS** |
| 3 | Charlie | Invoice #101 | False | 1 | 1 | **PASS** |
| 4 | Diana | Weekly Summary | True | 3 | 1 | **PASS** |
| 5 | Ethan | Welcome! | False | 2 | 2 | **PASS** |
| 6 | Fiona | Daily Standup | True | 1 | 0 | **PASS** |
| 7 | George | Alert: Disk usage | False | 3 | 0 | **PASS** |
| 8 | Hannah | Newsletter Issue 42 | True | 2 | 1 | **PASS** |
| 9 | Ian | Quick Question | False | 1 | 0 | **PASS** |
| 10 | Julia | Monthly Report | True | 4 | 2 | **PASS** |
| 11 | Kevin | Bug Report | False | 1 | 1 | **PASS** |
| 12 | Laura | Event Invitation | True | 2 | 0 | **PASS** |
| 13 | Michael | Receipt confirmation | False | 1 | 0 | **PASS** |
| 14 | Nina | Check-in | True | 3 | 1 | **PASS** |
| 15 | Oscar | Release notes v2.0 | False | 2 | 0 | **PASS** |
| 16 | Paula | Contract draft | True | 1 | 2 | **PASS** |
| 17 | Quinn | Schedule reminder | False | 1 | 0 | **PASS** |
| 18 | Rachel | Announcement | True | 2 | 1 | **PASS** |
| 19 | Sam | Thank you | False | 1 | 0 | **PASS** |
| 20 | Tina | Final Reminder | True | 3 | 0 | **PASS** |
| 21 | Victor | System Backup Status | False | 2 | 1 | **PASS** |

### 4. Input Non-Mutation Check
- `receiver_emails` and `attachments` lists verified to be unmutated after `send_email` execution -> **PASS**.

### 5. Native Test Runner Execution
- **Command**: `python3 -m unittest discover -s 'Automate Emails Daily' -p 'test_*.py' -v`
- **Result**: Ran 5 test suites (covering 21 oracle cross-checks) in 0.080s — OK (0 failures, 0 errors)
- **Status**: **PASS**

### 6. Failure Propagation Proof
- **Command**: `FORCE_WRONG=1 python3 work/R35-T003/check.py`
- **Output**: `FAIL: Smallest input return value mismatch: expected WRONG_RETURN, got None`
- **Exit Code**: `1` (Non-zero exit on assertion failure verified)
- **Status**: **PASS**
