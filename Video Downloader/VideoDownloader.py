"""Download the highest-resolution stream from a YouTube URL."""


def download_video(link: str) -> str:
    """Download the highest-resolution stream and return its saved file path."""
    from pytube import YouTube

    video = YouTube(link)
    stream = video.streams.get_highest_resolution()
    return stream.download()


def main() -> None:
    """Prompt for a YouTube URL and download its highest-resolution stream."""
    link = input("Enter the link: ")
    download_video(link)


if __name__ == "__main__":
    main()