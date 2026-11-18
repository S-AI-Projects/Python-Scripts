import tkinter
from time import strftime

TIME_FORMAT = '%H: %M: %S %p'
clockTime = None


def format_time(t_struct=None, strftime_func=strftime) -> str:
    """
    Format time according to the Digital Clock specification.

    Contract:
    - Preconditions:
        * Digital Clock/DigitalClock.py:2 establishes strftime import
        * Digital Clock/DigitalClock.py:4 establishes TIME_FORMAT = '%H: %M: %S %p'
    - Invariants:
        * Output is string of length 13: 'HH: MM: SS PP'
        * Structure: ^\\d{2}: \\d{2}: \\d{2} (AM|PM)$
        * Hour in [0, 23], Minute in [0, 59], Second in [0, 59]
        * AM for hour in [0, 11], PM for hour in [12, 23]
    """
    if t_struct is None:
        return strftime_func(TIME_FORMAT)
    return strftime_func(TIME_FORMAT, t_struct)


def time(label=None, scheduler=None, strftime_func=strftime):
    """
    Update clock label with current formatted time and schedule next update.

    Preconditions:
    - Digital Clock/DigitalClock.py:9 establishes time function
    - Digital Clock/DigitalClock.py:11 establishes '%H: %M: %S %p'
    """
    string = format_time(strftime_func=strftime_func)
    target_label = label if label is not None else clockTime
    if target_label is not None:
        target_label.config(text=string)
    if scheduler is not None:
        scheduler(1000, time)
    elif target_label is not None and hasattr(target_label, 'after'):
        target_label.after(1000, time)
    return string


def main():
    global top, clockTime
    top = tkinter.Tk()
    top.title('Digital Clock')
    # 0,0 makes the window non-resizable
    top.resizable(0, 0)

    clockTime = tkinter.Label(top, font=('courier new', 40),
                              background='red', foreground='black')
    clockTime.pack(anchor='center')
    time(label=clockTime)
    top.mainloop()


if __name__ == '__main__':
    main()
