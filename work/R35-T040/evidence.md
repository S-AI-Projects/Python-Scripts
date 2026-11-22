# R35-T040 Evidence

## Source behavior and preconditions

- Line 1 imports `Html2Image`; the tests replace this module with a mock.
- Line 3 creates the Html2Image instance.
- Lines 5-7 establish the interactive file path, image filename, and background
  inputs.
- Line 8 selects the CSS path only for a nonempty background.
- Lines 10-11 read the source HTML and call `screenshot()` with CSS and filename.
- Lines 13-14 read the source HTML and call `screenshot()` without CSS.

The original implementation asks for the values at import/run time. Tests mock
all three inputs, replace `Html2Image`, and use temporary HTML files. No browser
is started, screenshot is written, or live external service is contacted.

## Literal inputs and expected results

### Smallest valid HTML

- HTML file contents: `"<p>x</p>"`
- Background: `""`
- Filename: `"small.png"`
- Expected screenshot call:
  `screenshot("<p>x</p>", save_as="small.png")`
- Expected CSS: no `css_str` argument
- Expected call count: `1`
- Expected source file after run: still `"<p>x</p>"`

### Ordinary HTML

- HTML file contents: `"<html><body><h1>Hello</h1></body></html>"`
- Background: `"lightblue"`
- Filename: `"hello.png"`
- Independently formed CSS: `"body {background: lightblue;}"`
- Expected screenshot call:
  `screenshot("<html><body><h1>Hello</h1></body></html>", css_str="body {background: lightblue;}", save_as="hello.png")`
- Expected call count: `1`
- Expected source file after run: unchanged

Both expected call arguments and file contents matched actual results.

## Mutation evidence

The temporary copy changed exactly one condition:

```python
if len(background)>0:
```

to:

```python
if len(background) >= 0:
```

The mutated condition incorrectly enters the CSS branch for an empty
background. The original implementation passed
`test_smallest_html_with_empty_background_omits_css_argument`; the same named
test failed on the temporary mutant because its `screenshot()` call included an
unexpected `css_str` argument. The mutant existed only in a temporary directory
and was removed automatically.

## Tool versions and results

- Python: 3.15.2
- Test framework: standard-library `unittest`
- `Html2Image`: mocked; browser and screenshot generation were not run
- Original implementation: 2 tests passed
- Mutant check: same named regression test failed as expected

Exact command:

```text
python3 work/R35-T040/check.py
```

Final result: PASS
