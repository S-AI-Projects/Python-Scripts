# R35-T036 Evidence

## Focused refactor

The selected responsibility was HTTP status-message handling inside
`connection()`. The status-code extraction and printed message were moved into
the small private helper `_print_http_error(error)`. The public `connection`
arguments, success return type, failure return type, request call, and printed
messages remain unchanged.

## Literal inputs

Source precondition:

- `connection()` starts at `InstaDownloader/insta_down.py` line 21.
- Its default URL and timeout are established at line 21:
  `url='http://www.google.com/'`, `timeout=5`.
- The HTTP request is performed at line 23.
- Success output and `True` are established at lines 24-26.
- HTTP and connection failures are established at lines 27-30.

| Case | Literal input | Expected result |
|---|---|---|
| Smallest | Defaults: Google URL, timeout 5 | `requests.get` called once with the literal URL and timeout; response status is checked; return `True`; print success text |
| Ordinary | URL `https://example.com/check`, timeout `12` | `requests.get` called once with those literal values; return `True`; print success text |

HTTP status and connection exception cases were also verified:

- HTTP status `503`: return `False` and print `Checking internet connection failed, status code 503.`
- Mocked connection exception: return `False` and print `No internet connection available.`

## Expected versus actual

All four focused tests passed.

### Smallest input

- Expected: `get("http://www.google.com/", timeout=5)`, `True`, success output
- Actual: the mock was called exactly once with those arguments, returned `True`,
  and printed the expected success text.

### Ordinary input

- Expected: `get("https://example.com/check", timeout=12)`, `True`, success output
- Actual: the mock was called exactly once with those arguments, returned `True`,
  and printed the expected success text.

### HTTP error

- Expected: `False` and status `503` message
- Actual: `False` and exact status message

### Connection error

- Expected: `False` and no-connection message
- Actual: `False` and exact no-connection message

## Tool versions

- Python: 3.15.2
- Test framework: standard-library `unittest`
- HTTP dependency: `requests` was mocked; no live package or internet call was used
- Downloader dependency: `instaloader` was not imported by the focused AST test

## Test command

- `python3 work/R35-T036/check.py`
- Test count: 4
