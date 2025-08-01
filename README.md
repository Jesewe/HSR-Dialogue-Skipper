# Honkai Star Rail Dialogue Skipper

## Description

A Python script designed to automatically skip dialogue in _Honkai: Star Rail_ by simulating mouse clicks at specified screen coordinates. The script supports multiple screen resolutions and includes a failsafe to prevent unintended behavior. **Note**: Using third-party automation tools may risk account suspension or bans; use at your own discretion.

## Features

- **Auto-Clicking**: Toggles dialogue skipping with the F6 key.
- **Resolution Support**: Predefined coordinates for common resolutions (1280x720, 1366x768, 1600x900, 1920x1080, 2560x1440, 3840x2160) or custom coordinates.
- **Timeout**: Automatically stops after 120 seconds to prevent infinite clicking.
- **Admin Elevation**: Automatically requests administrator privileges for in-game functionality.
- **Colored Console**: Uses `colorama` for clear, colored status updates (Active/Inactive) in a single line.
- **Logging**: Records all actions and errors to `dialogue_skipper.log` for debugging.
- **Failsafe**: Move the mouse to the top-left corner to stop the script immediately.

## Installation

1. **Install Python**: Ensure Python 3.7 or later is installed ([Download Python](https://www.python.org/downloads/)).
2. **Install Dependencies**: Open a terminal and run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Download the Script**: Save `dialogue_skipper.py` to a directory.
4. **Run the Script**:
   - Double-click `dialogue_skipper.py` or run `python dialogue_skipper.py` in a terminal.
   - Approve the User Account Control (UAC) prompt for admin privileges.
5. **Usage**:
   - Select a screen resolution or enter custom coordinates.
   - Press F6 to start/stop auto-clicking (status updates in the console).
   - The script stops automatically after 120 seconds or when the mouse is moved to the top-left corner.
6. **Check Logs**: View `dialogue_skipper.log` in the script's directory for detailed activity logs.

**Note**: Coordinates are approximate and may need adjustment for your setup. Test custom coordinates if dialogue skipping fails.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
