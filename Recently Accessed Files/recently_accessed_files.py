import os
import datetime


def get_file_access_time(file_path):
    """Return the last access time of *file_path* as a float (Unix timestamp).

    Contract
    --------
    get_file_access_time
        Source line (precondition anchor): ``def get_file_access_time(file_path):``  # line 4
        Smallest valid input : file_path="" (any string; actual file mocked in tests)
        Ordinary input       : file_path="/home/user/document.txt"
        Result               : float — ``os.path.getatime(file_path)`` (last access timestamp)
        Dependencies         : os.path.getatime (file-system I/O — mock in tests)
        Mutation behaviour   : no input state mutated; purely reads file metadata

    Protected condition (mutation-resistant test target)
    ----------------------------------------------------
    The function calls ``os.path.getatime`` (access time), **not**
    ``os.path.getmtime`` (modification time) or ``os.path.getctime`` (change time).
    Swapping to ``getmtime`` is a plausible one-line mistake; the regression test
    distinguishes the two by mocking both with different values and asserting
    the return equals the access-time mock.

    Data anchor: ``recently_accessed_files = []``  # line 9 in get_recently_accessed_files
    """
    return os.path.getatime(file_path)   # precondition anchor: line 4


def get_recently_accessed_files(directory_path, time_threshold=None):

    recently_accessed_files = []          # data anchor: recently_accessed_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_access_time = get_file_access_time(file_path)

            if time_threshold is None or file_access_time >= time_threshold:
                recently_accessed_files.append(file_path)

    return sorted(recently_accessed_files, key=lambda file_path: get_file_access_time(file_path), reverse=True)


def main():

    # Get the directory path to search.
    directory_path = input("Enter the directory path to search: ")

    # Get the list of recently accessed files.
    recently_accessed_files = get_recently_accessed_files(directory_path)

    # Print the list of recently accessed files.
    print("List of recently accessed files:")
    for file_path in recently_accessed_files:
        print(f"{file_path}")

if __name__ == "__main__":
    main()
