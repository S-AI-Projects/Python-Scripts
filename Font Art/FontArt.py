import os
import sys

try:
    from pyfiglet import Figlet
except ImportError:
    Figlet = None


def render_font_art(text="Dhanush N", font="slant"):
    """Render the specified text into ASCII art using Figlet font.

    Args:
        text (str): The text string to render. Defaults to "Dhanush N".
        font (str): The Figlet font style name. Defaults to "slant".

    Returns:
        str: The rendered ASCII art string.

    Raises:
        ImportError: If pyfiglet is not installed.
    """
    global Figlet
    if Figlet is None:
        try:
            from pyfiglet import Figlet as _Figlet
            Figlet = _Figlet
        except ImportError:
            raise ImportError(
                "pyfiglet is required to render font art. Install it with 'pip install pyfiglet'."
            )
    fig = Figlet(font=font)
    return fig.renderText(text)


def display_font_art(text="Dhanush N", font="slant", cols=75, lines=30):
    """Clear screen, set console mode on Windows, and display rendered font art.

    Args:
        text (str): The text string to render. Defaults to "Dhanush N".
        font (str): The Figlet font style name. Defaults to "slant".
        cols (int): Number of columns for terminal width on Windows. Defaults to 75.
        lines (int): Number of lines for terminal height on Windows. Defaults to 30.

    Returns:
        str: The rendered ASCII art string printed to standard output.
    """
    if os.name == "nt":
        os.system("cls")
        os.system(f"mode con: cols={cols} lines={lines}")
    else:
        os.system("clear")

    art = render_font_art(text=text, font=font)
    print(art)
    return art


def main():
    display_font_art()


# Retain module-level attribute for backwards compatibility
text = Figlet(font="slant") if Figlet is not None else None

if __name__ == "__main__":
    main()
