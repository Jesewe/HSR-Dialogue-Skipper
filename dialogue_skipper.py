import pyautogui
import keyboard
import time
import threading
import ctypes
import sys
import os
import logging
from colorama import init, Fore, Style

# Initialize colorama for colored console output
init(autoreset=True)

# Configure logging to file only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='dialogue_skipper.log',
    filemode='a'
)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logging.error(f"Failed to check admin status: {e}")
        return False

def run_as_admin():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1)
            logging.info("Relaunched script with admin privileges")
            sys.exit()
        except Exception as e:
            logging.error(f"Failed to relaunch as admin: {e}")
            print(f"{Fore.RED}Error: Could not run as administrator. Please run manually with admin privileges.")
            sys.exit()

def select_resolution():
    resolutions = {
        "1": {"res": "1280x720", "x": 960, "y": 540},
        "2": {"res": "1366x768", "x": 1024, "y": 576},
        "3": {"res": "1600x900", "x": 1200, "y": 675},
        "4": {"res": "1920x1080", "x": 1350, "y": 750},
        "5": {"res": "2560x1440", "x": 1920, "y": 1080},
        "6": {"res": "3840x2160", "x": 2700, "y": 1500},
        "7": {"res": "Custom", "x": None, "y": None}
    }
    
    print(f"{Fore.CYAN}Select screen resolution:")
    for key, value in resolutions.items():
        print(f"{Fore.YELLOW}{key}: {value['res']}")
    
    choice = input(f"{Fore.CYAN}Enter choice (1-7): {Style.RESET_ALL}")
    while choice not in resolutions:
        print(f"{Fore.RED}Invalid choice. Please select 1-7.")
        choice = input(f"{Fore.CYAN}Enter choice (1-7): {Style.RESET_ALL}")
    
    if choice == "7":
        try:
            x = int(input(f"{Fore.CYAN}Enter X coordinate: {Style.RESET_ALL}"))
            y = int(input(f"{Fore.CYAN}Enter Y coordinate: {Style.RESET_ALL}"))
            logging.info(f"Selected custom resolution with coordinates ({x}, {y})")
            return x, y
        except ValueError as e:
            logging.error(f"Invalid coordinate input: {e}")
            print(f"{Fore.RED}Error: Invalid coordinates. Using default (1350, 750).")
            return 1350, 750
    else:
        logging.info(f"Selected resolution {resolutions[choice]['res']} with coordinates ({resolutions[choice]['x']}, {resolutions[choice]['y']})")
        return resolutions[choice]["x"], resolutions[choice]["y"]

def click_loop(x, y, stop_event):
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01
    start_time = time.time()
    while not stop_event.is_set() and (time.time() - start_time <= 120):
        pyautogui.click(x, y)
        time.sleep(0.01)
    logging.info("Click loop stopped")
    sys.stdout.write(f"\r{Fore.MAGENTA}Status: Inactive{Style.RESET_ALL}  ")
    sys.stdout.flush()

def main():
    run_as_admin()
    print(f"{Fore.GREEN}Honkai Star Rail Dialogue Skipper")
    print(f"{Fore.CYAN}Press F6 to start/stop the script. Script stops automatically after 120 seconds.")
    
    x, y = select_resolution()
    print(f"{Fore.YELLOW}Using coordinates: ({x}, {y})")
    print(f"{Fore.MAGENTA}Status: Inactive{Style.RESET_ALL}", end="  ")
    sys.stdout.flush()
    
    stop_event = threading.Event()
    click_thread = None
    
    def on_f6_press(e):
        nonlocal click_thread
        if not stop_event.is_set():
            stop_event.set()
            if click_thread:
                click_thread.join()
            sys.stdout.write(f"\r{Fore.MAGENTA}Status: Inactive{Style.RESET_ALL}  ")
            sys.stdout.flush()
            logging.info("Script stopped by F6")
        else:
            stop_event.clear()
            sys.stdout.write(f"\r{Fore.GREEN}Status: Active{Style.RESET_ALL}   ")
            sys.stdout.flush()
            logging.info("Script started")
            click_thread = threading.Thread(target=click_loop, args=(x, y, stop_event))
            click_thread.start()

    keyboard.on_press_key("f6", on_f6_press)
    
    try:
        keyboard.wait()  # Keep the script running until interrupted
    except KeyboardInterrupt:
        stop_event.set()
        if click_thread:
            click_thread.join()
        logging.info("Script terminated by KeyboardInterrupt")
        print(f"\n{Fore.RED}Script terminated.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()