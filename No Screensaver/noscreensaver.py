"""No Screensaver — keeps the screen awake by periodically moving the mouse.

Contract
--------
No Screensaver
    Source line (precondition anchor): ``import pyautogui``  # line 1
    Smallest valid input : interval_seconds=1, click_x=0, click_y=0
    Ordinary input       : interval_seconds=40, click_x=50, click_y=400
    Result               : None (side-effects only — sleep then click)
    Public interface     : ``keep_awake(interval_seconds, click_x, click_y)``
    Dependencies         : pyautogui (external GUI automation library)
    Mutation behaviour   : moves mouse cursor; no persistent state modified

The refactored responsibility extracted here is **click_position_from_args**:
previously the magic numbers ``50`` and ``400`` were embedded inline in the
loop body.  Naming them as parameters makes the purpose of each co-ordinate
explicit and the loop body easier to read at a glance.
"""

import pyautogui


def keep_awake(interval_seconds: int = 40, click_x: int = 50, click_y: int = 400) -> None:  # noqa: E501
    """Sleep *interval_seconds* then click at (*click_x*, *click_y*) once.

    Parameters
    ----------
    interval_seconds:
        Seconds to sleep before the click (smallest valid: 1).
    click_x:
        Horizontal screen co-ordinate for the click (smallest valid: 0).
    click_y:
        Vertical screen co-ordinate for the click (smallest valid: 0).

    Returns
    -------
    None
        Side-effects only: sleeps then moves the mouse cursor.
    """
    # precondition anchor: import pyautogui  # line 1
    pyautogui.sleep(interval_seconds)
    pyautogui.click(click_x, click_y)


def _run_loop(interval_seconds: int = 40, click_x: int = 50, click_y: int = 400) -> None:
    """Run the infinite keep-awake loop (not imported in tests)."""
    while True:
        keep_awake(interval_seconds, click_x, click_y)


if __name__ == "__main__":
    _run_loop()
