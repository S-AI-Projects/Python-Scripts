import os
import re


def compute_renamed_filename(filename: str, new_name: str, counter: int) -> str:
    """
    Construct the new filename using the base name, index counter, and original file extension.

    Extracted from lines 25-27 in original File_Renamer.py.

    Args:
        filename (str): The original filename.
        new_name (str): The new base name prefix.
        counter (int): The incrementing numeric index.

    Returns:
        str: The formatted new filename (e.g. 'new_name0.jpg').
    """
    filetype = filename.split('.')[-1]
    return new_name + str(counter) + '.' + filetype


def rename_files(directory, pattern, new_name):
    """
    Rename files in directory matching regex pattern using an incrementing counter.

    Contract:
    - Preconditions:
        - directory (str): Valid directory containing files (line 17: os.listdir(directory)).
        - pattern (str): Regular expression pattern (line 23: re.match(pattern, file)).
        - new_name (str): Prefix string for renamed files (line 27).
    - Result:
        Renames matching files via os.rename.
    """
    # List all files in the specified directory
    files = os.listdir(directory)
    counter = 0  # Initialize a counter for unique naming

    # Iterate over each file in the directory
    for file in files:
        # Check if the file matches the given pattern
        if re.match(pattern, file):
            new_filename = compute_renamed_filename(file, new_name, counter)
            # Rename the file with the new base name and counter
            os.rename(directory + '/' + file, directory + '/' + new_filename)
            counter += 1  # Increment the counter for the next file


def main():
    # Prompt the user for the directory path where files need to be renamed
    directory = input("Enter path: ")

    # Provide instructions on how to use regex for searching specific files
    print("To look for specific files, enter what you know, using .* for any characters you don't know.")
    print("For example: IMG.* will filter files that start with IMG")

    # Get the regex pattern to match files and the new base name for renaming
    pattern = input("Enter pattern: ")
    new_name = input("Enter the new name: ")

    # Call the function to rename files
    rename_files(directory, pattern, new_name)


if __name__ == "__main__":
    main()
