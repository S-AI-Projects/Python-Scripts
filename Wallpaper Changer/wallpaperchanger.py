import os
from datetime import datetime
try:
    import requests
except ImportError:
    requests = None
try:
    import numpy as np
except ImportError:
    np = None
try:
    import yfinance as yf
except ImportError:
    yf = None
try:
    import ctypes
except ImportError:
    ctypes = None

from PIL import Image, ImageFont, ImageDraw

# enable or disable any functionality
enable_time = True
enable_tickers = True
enable_quote = True

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

tickers = [
    ("^GSPC", "s&p500"),
    ("aapl", "aapl"),
    ("msft", "msft"),
    ("goog", "googl"),
    ("amzn", "amzn"),
    ("tsla", "tsla"),
    ("BTC-USD", "btc"),
    ("ETH-USD", "eth")
]


def add_margin(img, top, left, bottom, right, color):
    """
    Pad an image with border margins of specified thickness and color.

    Invariant Contract:
    - Precondition: img is a valid PIL Image instance with dimensions (width, height);
      top, left, bottom, right are non-negative integers (source line 57).
    - Invariant 1 (Dimension Preservation):
        result.width == img.width + left + right
        result.height == img.height + top + bottom
    - Invariant 2 (Mode Preservation):
        result.mode == img.mode
    - Invariant 3 (Sub-image Identity):
        result.crop((left, top, left + img.width, top + img.height)) == img
    - Invariant 4 (Input Immutability):
        The original img object's size and contents are unaltered.
    """
    width, height = img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(img.mode, (new_width, new_height), color)
    result.paste(img, (left, top))
    return result


def conv_to_size(path, path_to_save=None):
    z = Image.open(path)
    if z.size[0] / 1920 > z.size[1] / 1080:
        vres = z.size[0] * 1080 / 1920
        vres = vres - z.size[1]
        vres = int(vres / 2)
        res = add_margin(z, vres, 0, vres, 0, (0, 0, 0))
    else:
        hres = z.size[1] * 1920 / 1080
        hres = hres - z.size[0]
        hres = int(hres / 2)
        res = add_margin(z, 0, hres, 0, hres, (0, 0, 0))
    if path_to_save is not None:
        res.save(path_to_save)
    else:
        res.save(path)


def ret_change(ticker):
    if yf is None:
        return 0.0, 0.0
    x = yf.Ticker(ticker)
    z = x.history(period="3d")
    return (((z.iloc[-1]["Close"] - z.iloc[-2]["Close"]) / z.iloc[-2]["Close"]) * 100).round(2), z.iloc[-1]["Close"].round(2)


def main():
    folder_path = "path/to/folder/containing/images"
    if not os.path.isdir(folder_path):
        print(f"Directory not found: {folder_path}")
        return

    z_files = os.listdir(folder_path)
    if not z_files:
        return

    # opening random image
    idx = np.random.randint(len(z_files)) if np else 0
    path = os.path.join(folder_path, z_files[idx])
    z = Image.open(path)

    # check if in correct proportion, pad if it isnt
    if z.size[0] / z.size[1] > 1.78 or z.size[0] / z.size[1] < 1.76:
        conv_to_size(path)
        z = Image.open(path)

    # resizing to perfect resolution
    z = z.resize((1920, 1080))

    # start drawing
    I1 = ImageDraw.Draw(z)
    myFont = None
    if enable_quote and requests:
        try:
            myFont = ImageFont.truetype("path/to/.ttf/font/file", 20)
            l = "http://api.quotable.io/random"
            r = requests.get(l)
            r = r.json()
            text = r["content"] + " - " + r["author"]
            I1.text((10, 1050), text, font=myFont, fill=(255, 255, 255))
        except Exception:
            pass
    if enable_time:
        try:
            I1.text((1830, 1050), current_time, font=myFont, fill=(255, 255, 255))
        except Exception:
            pass
    if enable_tickers and yf:
        try:
            ticpos = 10
            for i, j in tickers:
                chn, pc = ret_change(i)
                I1.text((1670, ticpos), j, font=myFont, fill=(255, 255, 255))
                if chn >= 0:
                    I1.text((1750, ticpos), str(chn) + "%", font=myFont, fill=(0, 255, 0))
                    I1.text((1830, ticpos), str(pc), font=myFont, fill=(0, 255, 0))
                else:
                    I1.text((1750, ticpos), str(abs(chn)) + "%", font=myFont, fill=(255, 0, 0))
                    I1.text((1830, ticpos), str(pc), font=myFont, fill=(255, 0, 0))
                ticpos += 25
        except Exception:
            pass

    try:  # save as jpg
        save_path = "path/to/save/temp/wallpaper/in/.jpg/format"
        z.save(save_path, quality="high")
        if ctypes and hasattr(ctypes, 'windll'):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, save_path, 0)
    except Exception:
        save_path = "path/to/save/temp/wallpaper/in/.png/format"
        z.save("temp.png", quality="high")
        if ctypes and hasattr(ctypes, 'windll'):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, save_path, 0)


if __name__ == "__main__":
    main()
