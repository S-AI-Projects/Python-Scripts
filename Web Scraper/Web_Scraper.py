import requests
from bs4 import BeautifulSoup

# URL to scrape data from (Precondition Anchor: Web_Scraper.py line 5)
URL = "https://www.python.org/blogs/"


def fetch_webpage(url=URL):
    """
    Send a GET request to the target URL.

    Contract:
    - Precondition: url is a valid HTTP/HTTPS URL string (Precondition Anchor: Web_Scraper.py line 8).
    - Returns: requests.Response object.
    - External dependency: requests library.
    """
    return requests.get(url)


def extract_blog_titles(content):
    """
    Parse HTML content and extract text of all blog title elements.

    Contract:
    - Precondition: content is valid HTML as bytes or str (Precondition Anchor: Web_Scraper.py line 11).
    - Element selector: h2 tags with class 'blog-title' (Precondition Anchor: Web_Scraper.py line 14).
    - Returns: list of stripped title strings (List[str]).
    - Mutation: Pure function; does not mutate input or global state.
    """
    soup = BeautifulSoup(content, "html.parser")
    titles = soup.find_all("h2", class_="blog-title")
    return [title.get_text(strip=True) for title in titles]


def display_blog_titles(titles):
    """
    Print each title found with 1-based indexing.

    Contract:
    - Precondition: titles is an iterable of strings (Precondition Anchor: Web_Scraper.py line 17).
    - Observable mutation: prints formatted text to stdout.
    - Returns: None.
    """
    print("Python.org Blog Titles:\n")
    for i, title in enumerate(titles, start=1):
        print(f"{i}. {title}")


def save_blog_titles(titles, filename="blog_titles.txt"):
    """
    Save extracted blog titles to a text file, one per line.

    Contract:
    - Precondition: titles is an iterable of strings; filename is a valid writable path.
      (Precondition Anchor: Web_Scraper.py line 22).
    - Observable mutation: writes / overwrites filename with titles separated by newlines.
    - Returns: None.
    """
    with open(filename, "w", encoding="utf-8") as file:
        for title in titles:
            file.write(title + "\n")
    print(f"\nBlog titles saved to '{filename}'.")


def main(url=URL, filename="blog_titles.txt"):
    """
    Orchestrate scraping, displaying, and saving blog titles.

    Contract:
    - Preconditions: url defaults to URL (line 5), filename defaults to 'blog_titles.txt' (line 22).
    - Returns: list of extracted blog title strings.
    - Observable mutations: network GET, stdout prints, file write to filename.
    """
    response = fetch_webpage(url)
    titles = extract_blog_titles(response.content)
    display_blog_titles(titles)
    save_blog_titles(titles, filename)
    return titles


if __name__ == "__main__":
    main()
