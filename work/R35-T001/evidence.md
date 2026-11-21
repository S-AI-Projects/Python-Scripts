# R35-T001 Evidence

## Student Details
- **Student Name**: Nitesh Kumar
- **URN**: e26b07f0629
- **Task ID**: R35-T001 (Issue #1)
- **Repository**: S-AI-Projects/Python-Scripts
- **Assigned working branch**: student/e26b07f0629/R35-T001

## Target Item
- **Module**: `Web Scraper/Web_Scraper.py`
- **Target Functions**: `extract_blog_titles`, `save_blog_titles`, `display_blog_titles`, `fetch_webpage`, `main`
- **Source Fixture / Precondition Anchors**:
  - `URL = "https://www.python.org/blogs/"` (line 5): Base target URL precondition.
  - `response = requests.get(URL)` (line 8): HTTP GET request precondition.
  - `soup = BeautifulSoup(response.content, "html.parser")` (line 11): HTML parsing precondition.
  - `titles = soup.find_all('h2', class_='blog-title')` (line 14): Element selection precondition.
  - `print("Python.org Blog Titles:\n")` (line 17): Display stdout formatting precondition.
  - `with open("blog_titles.txt", "w") as file:` (line 22): Output file persistence precondition.

## Tool Versions
- **Python**: 3.15.0
- **Platform**: macOS (Darwin arm64)
- **requests**: 2.34.2
- **beautifulsoup4**: 4.15.0
- **Git Branch**: `student/e26b07f0629/R35-T001`

## Test Results and Evidence

### 1. Smallest Valid Input
- **Literal Input**: `'<h2 class="blog-title">A</h2>'`
- **Returned Value**:
  - Expected: `['A']`
  - Actual: `['A']`
  - Status: PASS
- **Observable File Mutation**:
  - Target file: `blog_titles.txt`
  - Expected content: `'A\n'`
  - Actual content: `'A\n'`
  - Status: PASS

### 2. Ordinary Input
- **Literal Input**:
  ```html
  <!DOCTYPE html>
  <html>
  <head><title>Python Blogs</title></head>
  <body>
    <div class="blog-posts">
      <h2 class="blog-title">Python 3.12 Released</h2>
      <p>Details about Python 3.12 release.</p>
      <h2 class="blog-title">PSF Grants Overview</h2>
      <p>Details about PSF grants.</p>
    </div>
  </body>
  </html>
  ```
- **Returned Value**:
  - Expected: `['Python 3.12 Released', 'PSF Grants Overview']`
  - Actual: `['Python 3.12 Released', 'PSF Grants Overview']`
  - Status: PASS
- **Observable File Mutation**:
  - Expected file content: `'Python 3.12 Released\nPSF Grants Overview\n'`
  - Actual file content: `'Python 3.12 Released\nPSF Grants Overview\n'`
  - Status: PASS
- **Observable Stdout Mutation**:
  - Contains `"Python.org Blog Titles:\n"`
  - Contains `"1. Python 3.12 Released"`
  - Contains `"2. PSF Grants Overview"`
  - Status: PASS

### 3. Domain Boundary and Repeated Values
- **Literal Input**:
  ```html
  <html><body>
    <h2 class="blog-title">Duplicate Title</h2>
    <h2 class="blog-title">  Duplicate Title  </h2>
    <h2 class="blog-title"></h2>
  </body></html>
  ```
- **Returned Value**:
  - Expected: `['Duplicate Title', 'Duplicate Title', '']`
  - Actual: `['Duplicate Title', 'Duplicate Title', '']`
  - Status: PASS (validates whitespace stripping and duplicate retention)

### 4. Native Test Runner Execution
- **Command**: `python3 -m unittest discover -s 'Web Scraper' -p 'test_*.py' -v`
- **Result**: Ran 8 tests in 0.003s — OK (0 failures, 0 errors)
- **Status**: PASS

### 5. Failure Propagation Proof
- **Command**: `FORCE_WRONG=1 python3 work/R35-T001/check.py`
- **Output**: `FAIL: Smallest input returned value mismatch: expected ['WRONG_TITLE'], got ['A']`
- **Exit Code**: `1` (Non-zero exit on assertion failure verified)
- **Status**: PASS
