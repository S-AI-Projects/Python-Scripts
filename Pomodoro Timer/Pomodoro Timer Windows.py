# Pomodoro Timer for Windows
"""Windows Pomodoro timer.

Public API: pomodoro_timer_windows(work_duration=25, break_duration=5, cycles=4).
Durations are in minutes; cycles is the number of work/break repetitions. The
function returns None, does not mutate caller-owned data, and prints progress
while sleeping and sounding an alert at each interval boundary. The script
entry point reads its three arguments from the console.

Dependencies: the standard-library time module and Windows-only winsound.
"""

import time
import winsound


def pomodoro_timer_windows(work_duration=25, break_duration=5, cycles=4):
    for cycle in range(cycles):
        print(f"Cycle {cycle + 1}/{cycles}: Start working for {work_duration} minutes.")
        time.sleep(work_duration * 60)
        winsound.Beep(1000, 1000)  # Sound an alert to indicate work period end
        print("Time's up! Take a break.")

        print(f"Break time! Relax for {break_duration} minutes.")
        time.sleep(break_duration * 60)
        winsound.Beep(1000, 1000)  # Sound an alert to indicate break period end
        print("Break is over! Back to work.")
    
    print("All cycles completed! Great job!")

if __name__ == "__main__":
    work_duration = int(input("Enter work duration in minutes (default is 25): ") or 25)
    break_duration = int(input("Enter break duration in minutes (default is 5): ") or 5)
    cycles = int(input("Enter number of cycles (default is 4): ") or 4)
    
    pomodoro_timer_windows(work_duration, break_duration, cycles)
