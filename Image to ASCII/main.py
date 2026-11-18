from PIL import Image

# ascii characters used to build the output text
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]


def calculate_new_dimensions(original_size: tuple[int, int], new_width: int = 100) -> tuple[int, int]:
    """
    Calculate proportional new dimensions preserving aspect ratio.

    Contract:
    - Precondition: original_size is (width, height) with width > 0, height > 0, new_width > 0.
    - Ratio calculation: ratio = height / width
    - Proportional height: int(new_width * ratio)
    - Returns: (new_width, new_height)
    """
    width, height = original_size
    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive")
    ratio = height / width
    new_height = int(new_width * ratio)
    return new_width, new_height


# resize image according to a new width
def resize_image(image, new_width=100):
    """
    Resize image according to new width while preserving aspect ratio.

    Preconditions:
    - Image to ASCII/main.py:6 establishes resize_image signature.
    """
    new_dims = calculate_new_dimensions(image.size, new_width=new_width)
    resized_image = image.resize(new_dims)
    return resized_image


# convert each pixel to grayscale
def grayify(image):
    grayscale_image = image.convert("L")
    return grayscale_image


# convert pixels to a string of ascii characters
def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters


def main(new_width=100):
    # attempt to open image from user-input
    path = input("Enter a valid pathname to an image:\n")
    try:
        image = Image.open(path)
    except Exception:
        print(path, " is not a valid pathname to an image.")
        return

    # convert image to ascii
    new_image_data = pixels_to_ascii(grayify(resize_image(image, new_width=new_width)))

    # format
    pixel_count = len(new_image_data)
    ascii_image = "\n".join([new_image_data[index:(index + new_width)] for index in range(0, pixel_count, new_width)])

    # print result
    print(ascii_image)

    # save result to "ascii_image.txt"
    try:
        with open("Image-To-ASCII/ascii_image.txt", "w") as f:
            f.write(ascii_image)
    except Exception:
        pass


if __name__ == "__main__":
    main()
