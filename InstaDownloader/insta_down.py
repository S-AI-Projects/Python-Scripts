try:
    import instaloader
    from instaloader import Post
except ImportError:
    instaloader = None
    Post = None

import requests
import sys


def print_banner():
    # Banner
    print(''' 

------------------ Instagram Images and Post Downloader ------------------
                            [Coded By Muneeb]

''')


def check_url_reachability(url: str, timeout: float = 5):
    """
    Subroutine: Probe target URL and return (is_connected: bool, status_message: str).
    Extracted from connection() to isolate network request/exception classification from output display.
    """
    try:
        req = requests.get(url, timeout=timeout)
        req.raise_for_status()
        return True, "You're connected to internet\n"
    except requests.HTTPError as e:
        status_code = e.response.status_code if getattr(e, 'response', None) is not None else "unknown"
        return False, "Checking internet connection failed, status code {0}.".format(status_code)
    except requests.ConnectionError:
        return False, "No internet connection available."
    except Exception:
        return False, "No internet connection available."


# #Function to check the internet connection
# #Got this from https://stackoverflow.com/a/24460981
def connection(url='http://www.google.com/', timeout=5):
    """
    Check the internet connection by issuing an HTTP GET to the specified URL.

    Contract:
    - Precondition: url is a valid HTTP/HTTPS URL string, timeout > 0 (source lines 25-39).
    - Refactored responsibility: network probe execution and exception classification are
      delegated to check_url_reachability(url, timeout).
    - Returns: bool (True if reachable and 2xx status, False otherwise).
    - Side-effects: Prints connectivity status message to standard output.
    """
    is_connected, message = check_url_reachability(url, timeout=timeout)
    print(message)
    return is_connected


def download_insta_post(loader, target_username, post_code):
    if loader is None:
        raise RuntimeError("instaloader package is not installed")
    profile = instaloader.Profile.from_username(loader.context, target_username)
    post = Post.from_shortcode(loader.context, post_code)
    loader.download_post(post, target=target_username)


def main():
    print_banner()
    if connection() == True:
        if instaloader is None:
            print("Error: instaloader is not installed.")
            sys.exit(1)
        # Create an instance of Instaloader
        L = instaloader.Instaloader()
        try:
            while True:
                a = "Press 'A' to download an instagram post from a private profile.\nPress 'B' to download an instagram post from a public profile.\nPress 'Q' to exit."
                print(a)
                select = str(input("\nInstaSave > ")).upper()
                try:
                    if select == 'A':
                        username = input("Enter your IG username: ")
                        password = input("Enter your IG password: ")
                        L.login(username, password)
                        t_username = input("Enter the target insta username: ")
                        post_code = input("Enter the post code for the media (Please don't enter the URL - only code) : ")
                        download_insta_post(L, t_username, post_code)
                        print("Post downloaded successfully")
                    elif select == 'B':
                        t_username = input("Enter the target insta username: ")
                        post_code = input("Enter the post code for the media (Please don't enter the URL - only code) : ")
                        download_insta_post(L, t_username, post_code)
                        print("Post downloaded successfully")
                    elif select == 'Q':
                        sys.exit()
                    else:
                        sys.exit()
                except KeyboardInterrupt:
                    print("Programme Interrupted")
        except KeyboardInterrupt:
            print("\nProgramme Interrupted")
    else:
        sys.exit()


if __name__ == "__main__":
    main()
