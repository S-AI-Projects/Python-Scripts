# Importing required modules
from PIL import Image
from glob import glob


# Supported inputs include PNG images of any size that Pillow can open.
# Source lines 10-13 establish opening, RGB conversion, and JPEG saving.
def convert_png_to_jpg(img_file, quality=95):
    img = Image.open(img_file)
    rgb_img = img.convert("RGB")
    output_file = img_file.replace("png", "jpg")
    rgb_img.save(output_file, quality=quality)
    return output_file


def convert_all_png(pattern="*.png", quality=95):
    png_files = glob(pattern)
    print(png_files)

    for img_file in png_files:
        convert_png_to_jpg(img_file, quality)


if __name__ == "__main__":
    convert_all_png()
