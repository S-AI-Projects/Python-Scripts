import glob
from PIL import Image


def make_gif(frame_folder, output_filepath="my_awesome.gif"):
    """
    Compile JPG images from frame_folder into an animated GIF.

    Contract:
    - Preconditions:
        - frame_folder (str): Directory containing at least 1 '.JPG' image.
          Precondition established by line 5 in original source: `frame_one = frames[0]`,
          which requires len(frames) >= 1.
        - output_filepath (str, optional): Target output path for the generated GIF.
          Defaults to "my_awesome.gif".
    - Returns:
        str: Path to the generated GIF file (output_filepath).
    - Mutation:
        Pure operation with respect to input parameters; does not mutate source images.
    - Representative Result:
        Given a folder containing 1 image ['frame0.JPG'], saves 'my_awesome.gif'
        with 1 base frame, format='GIF', duration=100ms, and loop=0.
    """
    frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*.JPG")]
    if not frames:
        raise ValueError(f"No JPG images found in {frame_folder} to create GIF.")
    frame_one = frames[0]
    frame_one.save(output_filepath, format="GIF", append_images=frames,
               save_all=True, duration=100, loop=0)
    return output_filepath


if __name__ == "__main__":
    make_gif("/path/to/images")
