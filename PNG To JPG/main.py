# Importing required module
import os
from PIL import Image
from glob import glob


def convert_png_to_jpg(img_file: str, quality: int = 95) -> str:
    """
    Convert a single PNG image file to JPEG format.

    Boundary & Contract Specification:
    - Precondition: img_file must be an existing valid file path (source line 21).
    - Supported inputs:
      - Smallest valid input: 1x1 pixel PNG (e.g. RGB or RGBA mode).
      - Ordinary input: Standard dimensional PNG (e.g. 100x100 pixel PNG or example.png).
      - Supported quality range: integer 1 <= quality <= 100 (default 95).
    - Unsupported / Error conditions:
      - Non-existent file path: raises FileNotFoundError.
      - Unsupported quality (< 1 or > 100): raises ValueError.
    - Behavior: Opens the image, converts to 'RGB' mode, and saves as .jpg with specified quality.
    - Output: Returns the generated .jpg file path string.
    """
    if not os.path.exists(img_file):
        raise FileNotFoundError(f"Source file not found: {img_file}")
    if not (1 <= quality <= 100):
        raise ValueError(f"Quality must be between 1 and 100, got {quality}")

    img = Image.open(img_file)  # Opening the image file
    rgb_img = img.convert("RGB")  # Converting it into RGB
    target_file = img_file[:-4] + ".jpg" if img_file.lower().endswith(".png") else img_file.replace("png", "jpg")
    rgb_img.save(target_file, quality=quality)  # Saving the img as .jpg
    return target_file


def convert_all_png(pattern: str = "*.png", quality: int = 95):
    """
    Find and convert all matching PNG files.
    """
    files = glob(pattern)
    print(files)
    converted = []
    for img_file in files:
        converted.append(convert_png_to_jpg(img_file, quality=quality))
    return converted


if __name__ == "__main__":
    convert_all_png("*.png")
