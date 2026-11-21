# R35-T004 Evidence

## Student Details
- **Student Name**: Nitesh Kumar
- **URN**: e26b07f0629
- **Task ID**: R35-T004 (Issue #4)
- **Repository**: S-AI-Projects/Python-Scripts
- **Assigned working branch**: student/e26b07f0629/R35-T004

## Target Item
- **Module**: `Profanity Checker/ProfanityChecker.py`
- **Target Item**: `Profanity Checker` / `analyze_text`, `classify_sentiment`, `preprocess_text`
- **Precondition Anchors**:
  - `SentimentIntensityAnalyzer`: VADER sentiment analyzer initialization
  - `word_tokenize`: NLTK tokenization
  - `WordNetLemmatizer`: WordNet lemmatization
  - `stopwords.words('english')`: English stopword filtering
  - `https://www.purgomalum.com/service/json?text=`: Purgomalum profanity checking API

## Documented Invariants Justification
1. **Invariant 1 (Score Boundedness)**:
   For any text input from the domain, VADER compound polarity score is mathematically constrained:
   `-1.0 <= compound <= 1.0`, with component ratios `0.0 <= pos, neg, neu <= 1.0`.
2. **Invariant 2 (Sentiment Partition Completeness & Exclusivity)**:
   The compound polarity space $[-1.0, 1.0]$ is completely partitioned into 5 mutually exclusive label intervals:
   - $(0.5, 1.0] \implies$ `'Very Positive'`
   - $(0.0, 0.5] \implies$ `'Positive'`
   - $[0.0, 0.0] \implies$ `'Neutral'`
   - $[-0.5, 0.0) \implies$ `'Negative'`
   - $[-1.0, -0.5) \implies$ `'Very Negative'`
   Every score maps to exactly one valid label.
3. **Invariant 3 (Preprocessing Idempotency)**:
   `preprocess_text(preprocess_text(text)) == preprocess_text(text)`. Repeated passes over filtered text produce identical results.
4. **Invariant 4 (Token Reduction Invariant)**:
   Filtering stopwords and punctuation never increases the token count: `len(word_tokenize(filtered)) <= len(word_tokenize(original))`.
5. **Invariant 5 (Input Immutability)**:
   All string manipulation operations are purely functional and leave the caller's input string unmutated.

## Tool Versions
- **Python**: 3.15.0
- **Platform**: macOS (Darwin arm64)
- **nltk**: 3.10.4
- **vaderSentiment**: 3.3.2
- **Git Branch**: `student/e26b07f0629/R35-T004`

## Test Results and Evidence

### 1. Smallest Supported Input
- **Input Text**: `"Good"`
- **Expected Filtered Text**: `"good"`
- **Actual Filtered Text**: `"good"`
- **Expected Compound Score**: `0.4404`
- **Actual Compound Score**: `0.4404`
- **Expected Sentiment Label**: `"Positive"`
- **Actual Sentiment Label**: `"Positive"`
- **Status**: **PASS**

- **Smallest Empty Input**: `""`
- **Filtered Text**: `""`
- **Compound Score**: `0.0`
- **Sentiment Label**: `"Neutral"`
- **Status**: **PASS**

### 2. Ordinary Valid Input
- **Input Text**: `"I love programming in Python. It is wonderful and clean."`
- **Filtered Text**: `"love programming python . wonderful clean ."`
- **Compound Score**: `0.8519`
- **Sentiment Label**: `"Very Positive"`
- **Status**: **PASS**

### 3. 100 Bounded Property-Based Invariant Cases
- **Seed**: `42`
- **Tested**: 100 dynamically generated sentences composed of positive, negative, neutral, stopwords, and punctuation.
- **Results**:
  - Score Boundedness: 100/100 within $[-1.0, 1.0]$ -> **PASS**
  - Partition Exclusivity: 100/100 exactly matched label thresholds -> **PASS**
  - Idempotency: 100/100 passes identical -> **PASS**
  - Token Reduction: 100/100 filtered token counts $\le$ original counts -> **PASS**
  - Input Immutability: 100/100 inputs unmodified -> **PASS**

### 4. Native Test Runner Execution
- **Command**: `python3 -m unittest discover -s 'Profanity Checker' -p 'test_*.py' -v`
- **Result**: Ran 5 test suites (covering 100 property cases) in 1.088s — OK (0 failures, 0 errors)
- **Status**: **PASS**

### 5. Failure Propagation Proof
- **Command**: `FORCE_WRONG=1 python3 work/R35-T004/check.py`
- **Output**: `FAIL: Smallest valid input compound mismatch: expected -99.9, got 0.4404`
- **Exit Code**: `1` (Non-zero exit on assertion failure verified)
- **Status**: **PASS**
