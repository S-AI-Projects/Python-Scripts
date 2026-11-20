try:
    import win32api
    import win32con
except ImportError:
    win32api = None
    win32con = None

import time
import random


def click(x, y):
    """
    Simulate a left mouse click at screen coordinates (x, y).

    Complexity Specification:
    - Input Size Variable:
        - For a single invocation: Input coordinate magnitude / constant bounds [0, 100].
        - For a stream of operations: N = number of sequential click invocations.
    - Theoretical Complexity:
        - Time Complexity: O(1) constant time per click. Performs exactly 3 fixed OS API operations
          (1 SetCursorPos + 2 mouse_event calls).
        - Space Complexity: O(1) auxiliary memory.
    - Empirical Scaling:
        - Scaling across batch sizes N is strictly O(N) linear in operation count.

    Contract:
    - Preconditions:
        - x, y (int): Screen pixel coordinates, typically in [0, 100] (lines 3 & 8 in original source).
    - Result:
        - Dispatches left mouse button down and up events at (x, y).
        - Returns tuple (x, y) coordinates clicked.
    """
    if win32api is not None:
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    return (x, y)


def main():
    while True:
        click(random.randint(0, 100), random.randint(0, 100))
        time.sleep(15)


if __name__ == "__main__":
    main()
