"""Screenshot to Text — extracts text from images using OCR (pytesseract).

Complexity note
---------------
``extract_text_from_image(img)``
    Input-size variable: ``n = img.width * img.height`` (total pixels).
    The function's own Python code (try/except + return) is O(1) in ``n``.
    All measurable work is delegated to ``pytesseract.image_to_string``,
    whose OCR engine is empirically observed to scale at least linearly in
    pixel count — this is an observation, not a worst-case proof.
    Distinguish algorithm operations (OCR pixel scan) from process startup
    (tesseract binary launch, model load) which is a constant per-call overhead.
"""

import pytesseract
from PIL import Image, ImageGrab
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar


def extract_text_from_image(img):
    """Extract text from a PIL Image using pytesseract OCR.

    Contract
    --------
    extract_text_from_image
        Source line (precondition anchor): ``def extract_text_from_image(img):``  # line 6
        Smallest valid input : ``img = Image.new("RGB", (1, 1))``  → ``""`` or ``"\\n"``
        Ordinary input       : ``img = Image.new("RGB", (100, 100))`` → ``""`` or text string
        Result               : str (extracted text) on success; ``None`` on any exception
        Dependencies         : pytesseract.image_to_string (external OCR binary — mock in tests)
        Mutation behaviour   : no input state mutated; no persistent state

    Complexity observation (input-size n = img.width * img.height pixels):
        Python wrapper: O(1) — try/except + return only.
        Delegated OCR work: empirically O(n) in pixel count (observed, not proven).
        Process startup overhead (tesseract binary + model load) is constant per call.
    """
    try:
        text = pytesseract.image_to_string(img)   # precondition anchor: line 6
        return text
    except Exception as e:
        print(e)
        return None


def select_image_file():  # Upload a Image file
    img_path = filedialog.askopenfilename(title="Select Screenshot", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
    if img_path:
        img = Image.open(img_path)
        display_extracted_text(img)

def paste_image_from_clipboard():   # Take partial screenshot (Windows + shift + S) it will be saved in clipboard.
    try:
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            display_extracted_text(img)
        else:
            messagebox.showwarning("Error", "No image found in the clipboard.")
    except Exception as e:
        messagebox.showerror("Error", f"Error accessing clipboard: {e}")

def capture_screenshot():  # Takes entire screen screenshot
    try:
        img = ImageGrab.grab()
        display_extracted_text(img)
    except Exception as e:
        messagebox.showerror("Error", f"Error capturing screenshot: {e}")

def display_extracted_text(img):  # Displaying extracted text from pytesseract
    text = extract_text_from_image(img)
    if text:
        text_display.delete(1.0, tk.END)
        text_display.insert(tk.END, text)
    else:
        messagebox.showwarning("Error", "No text could be extracted or an error occurred.")

def main():
    global text_display

    root = tk.Tk()
    root.title("Text Extractor with Python")

    text_frame = tk.Frame(root)
    text_frame.pack(pady=10)

    scrollbar = Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_display = Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15, width=60)
    text_display.pack()

    scrollbar.config(command=text_display.yview)

    btn_select_file = tk.Button(root, text="Select Image File", command=select_image_file, width=30)
    btn_select_file.pack(pady=10)

    btn_paste_clipboard = tk.Button(root, text="Paste Image from Clipboard", command=paste_image_from_clipboard, width=30)
    btn_paste_clipboard.pack(pady=10)

    btn_capture_screenshot = tk.Button(root, text="Capture Full Screen Screenshot", command=capture_screenshot, width=30)
    btn_capture_screenshot.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
