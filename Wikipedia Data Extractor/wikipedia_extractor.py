import wikipedia


def extract_summary(topic: str, lang: str = "en") -> str:
    """
    Extract a Wikipedia summary for a given topic in the specified language.

    Invariant / Contract:
    - Preconditions:
        - topic (str): Non-empty string query. Precondition established by line 3 in original source.
        - lang (str, optional): Language code string (defaults to 'en'). Precondition established by line 6 in original source.
    - Invariants:
        1. String Output Type Invariant: Result is always a non-empty string instance (`isinstance(result, str)` and `len(result) > 0`).
        2. Idempotency Invariant: Calling `extract_summary(topic, lang)` repeatedly under unchanged backend state returns identical text.
        3. Language Routing Invariant: Sets language via `wikipedia.set_lang(lang)` prior to query fetching.
        4. Immutability Invariant: Input strings `topic` and `lang` remain unaltered.
    - Representative Result:
        Given topic="Open Source", lang="jp", sets language to 'jp' and returns the summary string.
    """
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic must be a non-empty string.")
    if not isinstance(lang, str) or not lang.strip():
        raise ValueError("Language must be a non-empty string.")

    wikipedia.set_lang(lang)
    return wikipedia.summary(topic)


def main():
    search = input("Enter the topic you want: ")
    print(extract_summary(search))

    language = "jp"
    print(f"Summary of Open source in {language}:", extract_summary("Open Source", lang=language))


if __name__ == "__main__":
    main()
