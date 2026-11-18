import cv2
import numpy as np


def remove_background(img: np.ndarray, threshold: int = 250) -> np.ndarray:
    """
    Remove background from a 3-channel BGR image and return a 4-channel BGRA image with transparency.

    Boundary & Contract Specification:
    - Precondition: `img` must be a valid non-empty 3-channel BGR numpy array of dtype uint8 (source line 1).
    - Supported inputs:
      - Smallest valid input: 1x1 3-channel BGR image array (shape=(1, 1, 3)).
      - Ordinary input: Standard dimensional BGR image (e.g. shape=(100, 100, 3) or source person.png).
      - Supported threshold range: integer 0 <= threshold <= 255 (default 250).
    - Unsupported / Error conditions:
      - Empty array, None, or zero-dimension image (height == 0 or width == 0): raises ValueError.
      - Non-3-channel image (e.g. 2D grayscale or 4-channel): raises ValueError.
      - Unsupported threshold (< 0 or > 255): raises ValueError.
    - Behavior:
      - Converts BGR to grayscale.
      - Thresholds input image as mask and negates mask.
      - Applies morphology open and close using a 3x3 kernel.
      - Blurs and stretches the mask to anti-alias the alpha channel.
      - Attaches the resulting mask as the 4th (alpha) channel in a BGRA image.
    - Output:
      - Returns a 4-channel BGRA numpy.ndarray of shape (H, W, 4) with dtype uint8.
    """
    if img is None:
        raise ValueError("Input image cannot be None")
    if not isinstance(img, np.ndarray):
        raise TypeError("Input image must be a numpy ndarray")
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError(f"Input image must have 3 channels (BGR), got shape {img.shape}")
    if img.shape[0] == 0 or img.shape[1] == 0:
        raise ValueError(f"Input image dimensions must be non-zero, got shape {img.shape}")
    if not (0 <= threshold <= 255):
        raise ValueError(f"Threshold must be between 0 and 255, got {threshold}")

    # convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # threshold input image as mask
    mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)[1]

    # negate mask
    mask = 255 - mask

    # apply morphology to remove isolated extraneous noise
    # use borderconstant of black since foreground touches the edges
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # anti-alias the mask -- blur then stretch
    # blur alpha channel
    mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=2, sigmaY=2, borderType=cv2.BORDER_DEFAULT)

    # linear stretch so that 127.5 goes to 0, but 255 stays 255
    mask = (2 * (mask.astype(np.float32)) - 255.0).clip(0, 255).astype(np.uint8)

    # put mask into alpha channel
    result = img.copy()
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = mask
    return result


def main():
    # import image
    img = cv2.imread('person.png')
    if img is None:
        print("Image 'person.png' not found.")
        return

    # convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # threshold input image as mask
    mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]

    # negate mask
    mask = 255 - mask

    # apply morphology to remove isolated extraneous noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # anti-alias the mask -- blur then stretch
    mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=2, sigmaY=2, borderType=cv2.BORDER_DEFAULT)
    mask = (2 * (mask.astype(np.float32)) - 255.0).clip(0, 255).astype(np.uint8)

    # put mask into alpha channel
    result = img.copy()
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = mask

    # save resulting masked image
    cv2.imwrite('person_transp_bckgrnd.png', result)

    # display result
    cv2.imshow("INPUT", img)
    cv2.imshow("GRAY", gray)
    cv2.imshow("MASK", mask)
    cv2.imshow("RESULT", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
