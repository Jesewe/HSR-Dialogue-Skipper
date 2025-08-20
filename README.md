# Honkai Star Rail Dialogue Skipper

## Description

A Python script designed to automate dialogue skipping in _Honkai: Star Rail_ by simulating mouse clicks at specified screen coordinates. The script offers a CLI interface with configurable settings, multiple resolution support, and safety features to prevent unintended behavior. **Note**: Using third-party automation tools may risk account suspension or bans; use at your own discretion.

## Features

- **Auto-Clicking**: Toggle dialogue skipping with a configurable hotkey (default: F6).
- **Pause/Resume**: Pause or resume clicking with a dedicated hotkey (default: F7).
- **Emergency Stop**: Instantly stop the script with a hotkey (default: F8) or by moving the mouse to the top-left corner (PyAutoGUI failsafe).
- **Resolution Support**: Predefined coordinates for common resolutions (1280x720, 1366x768, 1600x900, 1920x1080, 2560x1440, 3840x2160) or custom coordinates.
- **Configurable Settings**:
  - Adjustable click interval (default: 0.01s, ~100 clicks/sec).
  - Auto-stop timer (default: 120 seconds) to prevent infinite clicking.
  - Toggleable click counter and elapsed time display.
- **Admin Elevation**: Automatically requests administrator privileges for in-game functionality (Windows only).
- **Colored Console**: Uses `colorama` for clear, color-coded status updates (Active/Paused/Ready) with click statistics and remaining time.
- **Configuration Persistence**: Saves settings (hotkeys, coordinates, etc.) to `dialogue_skipper_config.json` for reuse.
- **Logging**: Records actions, errors, and session statistics to `dialogue_skipper.log` for debugging.
- **Interactive Menu**: User-friendly menu for configuring click positions, hotkeys, and other settings.

## Installation

1. **Install Python**: Ensure Python 3.7 or later is installed ([Download Python](https://www.python.org/downloads/)).
2. **Install Dependencies**: Open a terminal and run:
   ```bash
   pip install pyautogui keyboard colorama
   ```
3. **Download the Script**: Save `dialogue_skipper.py` to a directory.
4. **Run the Script**:
   - Double-click `dialogue_skipper.py` or run `python dialogue_skipper.py` in a terminal.
   - Approve the User Account Control (UAC) prompt for admin privileges (Windows only).
5. **Usage**:
   - From the main menu, select options to configure click position, hotkeys, or view settings.
   - Choose a predefined resolution or enter custom coordinates.
   - Press the start/stop hotkey (default: F6) to begin auto-clicking.
   - Use the pause/resume hotkey (default: F7) to temporarily halt clicking.
   - Press the emergency stop hotkey (default: F8) or move the mouse to the top-left corner to stop immediately.
   - Monitor real-time status (click count, rate, elapsed time) in the console.
   - The script stops automatically after the configured auto-stop time (default: 120 seconds).
6. **Check Logs**: View `dialogue_skipper.log` in the script's directory for detailed activity logs and error details.
7. **Configuration**: Adjust settings via the interactive menu or edit `dialogue_skipper_config.json` directly.

**Note**: Coordinates are approximate and may require adjustment for your setup. Test custom coordinates if dialogue skipping fails. Ensure the game is running in the correct resolution.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
