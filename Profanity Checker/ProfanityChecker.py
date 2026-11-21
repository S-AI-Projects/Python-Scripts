"""
Profanity Checker and Sentiment Analysis Tool.

Documented Property Invariants:
1. Invariant 1 (Score Boundedness):
   For all valid text inputs, VADER compound polarity score is strictly bounded:
   -1.0 <= compound <= 1.0, with pos, neg, neu in [0.0, 1.0].
2. Invariant 2 (Sentiment Partition Completeness & Exclusivity):
   Every compound score maps deterministically to exactly one of 5 mutually exclusive labels:
   - compound > 0.5: 'Very Positive'
   - 0.0 < compound <= 0.5: 'Positive'
   - compound == 0.0: 'Neutral'
   - -0.5 <= compound < 0.0: 'Negative'
   - compound < -0.5: 'Very Negative'
3. Invariant 3 (Preprocessing Idempotency):
   preprocess_text(preprocess_text(text)) == preprocess_text(text).
4. Invariant 4 (Token Reduction Invariant):
   len(word_tokenize(preprocess_text(text))) <= len(word_tokenize(text)).
5. Invariant 5 (Input Non-Mutation):
   The text processing operations are pure and do not mutate the input arguments.
"""

import os
import sys
import csv
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Add workspace nltk_data fallback if present
_workspace_nltk = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "nltk_data"))
if os.path.exists(_workspace_nltk) and _workspace_nltk not in nltk.data.path:
    nltk.data.path.insert(0, _workspace_nltk)


def preprocess_text(text: str) -> str:
    """
    Tokenize, lowercase, strip English stopwords, and lemmatize text.

    Contract:
    - Precondition: text is a string.
    - Postcondition Invariant: Output is lowercase, contains no stopwords, and is idempotent.
    """
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    filtered_tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens if not w.lower() in stop_words]
    return ' '.join(filtered_tokens)


def check_profanity(filtered_text: str):
    """
    Check for profanity using the Purgomalum API.
    """
    response = requests.get("https://www.purgomalum.com/service/json?text=" + filtered_text)
    return response.json()


def classify_sentiment(compound_score: float) -> str:
    """
    Classify a VADER compound score into one of five mutually exclusive sentiment labels.

    Contract:
    - Precondition: -1.0 <= compound_score <= 1.0
    - Postcondition: Returns exactly one valid label:
        'Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative'
    """
    if compound_score > 0.5:
        return 'Very Positive'
    elif compound_score > 0:
        return 'Positive'
    elif compound_score == 0:
        return 'Neutral'
    elif compound_score < -0.5:
        return 'Very Negative'
    else:
        return 'Negative'


def analyze_sentiment(text: str):
    """
    Analyze sentiment of the given text using VADER and determine its sentiment label.
    """
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    sentiment_label = classify_sentiment(sentiment_scores['compound'])
    return sentiment_scores, sentiment_label


def analyze_text(text: str):
    """
    End-to-end text analysis returning structured results.
    """
    filtered = preprocess_text(text)
    scores, label = analyze_sentiment(text)
    return {
        "text": text,
        "filtered_text": filtered,
        "scores": scores,
        "sentiment_label": label,
    }


def main():
    import speech_recognition as sr
    import tkinter as tk
    from tkinter import filedialog

    try:
        nltk.download('wordnet', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except Exception:
        pass

    # Initialize the recognizer
    r = sr.Recognizer()

    # Ask the user whether to record from the microphone or select a file
    root = tk.Tk()
    root.withdraw()
    mode = input("Enter 'mic' to record from microphone or 'file' to select a file: ")

    text = ""
    if mode == 'mic':
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print("You said: " + text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    elif mode == 'file':
        file_path = filedialog.askopenfilename()
        print("Selected file:", file_path)
        with sr.AudioFile(file_path) as source:
            audio = r.record(source)
        try:
            text = r.recognize_google(audio)
            print("Transcription: " + text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    else:
        print("Invalid mode selected.")

    if not text:
        return

    filtered_text = preprocess_text(text)

    # Check for profanity in the text using the API
    try:
        result = check_profanity(filtered_text)
        if result.get('result') == filtered_text:
            print("No profanity detected!")
        else:
            print("Profanity detected!")
            print("Censored text: " + str(result.get('result')))
    except Exception as e:
        print(f"Profanity check failed: {e}")

    sentiment_scores, sentiment_label = analyze_sentiment(text)

    # Print sentiment scores
    print("\nSentiment Scores:")
    for key, value in sentiment_scores.items():
        print(key, ': ', value)
    print("\nSentiment Label: " + sentiment_label)

    # Write input and output to CSV file
    with open('profanitycheckeroutput.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Input Text', 'Filtered Text', 'Positive Score', 'Negative Score', 'Neutral Score', 'Compound Score', 'Sentiment Label'])
        writer.writerow([text, filtered_text, sentiment_scores['pos'], sentiment_scores['neg'], sentiment_scores['neu'], sentiment_scores['compound'], sentiment_label])


if __name__ == "__main__":
    main()
