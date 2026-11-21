# Pomodoro Timer
## 📋 Overview
The Pomodoro Timer is a productivity tool designed to help you manage your time efficiently using the Pomodoro Technique. It splits your work into intervals—typically 25 minutes of focused work followed by a 5-minute break. This cycle helps to boost focus and prevent burnout by encouraging regular breaks. The script is cross-platform, supporting both Windows and macOS/Linux.

## ✨ Features
- **Customizable Work and Break Durations:** Set your preferred time for work and break sessions.
- **Support for Multiple Cycles:** Run multiple Pomodoro sessions in a row.
- **Platform-Specific Alerts:**
- **Windows:** Uses sound alerts (winsound) to notify users when a session is complete.
- **macOS/Linux:** Uses terminal beep commands for notifications.

## Running the script

From the `Pomodoro Timer` directory, run the script for your platform:

```text
# Windows
python "Pomodoro Timer Windows.py"

# macOS/Linux
python3 "Pomodoro Timer MacOS Linux.py"
```

The Windows script prompts for work duration, break duration, and cycle count.
Its public function is `pomodoro_timer_windows(work_duration=25,
break_duration=5, cycles=4)`; durations are in minutes. It returns `None`,
prints progress, waits between intervals, and uses Windows `winsound` alerts.
