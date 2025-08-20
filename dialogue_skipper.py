import pyautogui
import keyboard
import time
import threading
import ctypes
import sys
import os
import logging
import json
from datetime import datetime
from colorama import init, Fore, Style, Back
from dataclasses import dataclass, asdict
from typing import Dict, Tuple, Optional

# Initialize colorama for colored console output
init(autoreset=True)

@dataclass
class Config:
    """Configuration class for the dialogue skipper"""
    # Hotkeys
    start_stop_key: str = "f6"
    pause_key: str = "f7"
    emergency_stop_key: str = "f8"
    
    # Click settings
    click_interval: float = 0.01
    auto_stop_time: int = 120
    
    # Coordinates
    click_x: int = 1350
    click_y: int = 750
    
    # UI settings
    show_click_counter: bool = True
    show_elapsed_time: bool = True
    
    # Audio feedback (if available)
    audio_feedback: bool = False

class DialogueSkipper:
    def __init__(self):
        self.config = self.load_config()
        self.setup_logging()
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.click_thread: Optional[threading.Thread] = None
        self.is_active = False
        self.is_paused = False
        self.click_count = 0
        self.start_time = 0
        self.status_lock = threading.Lock()
        
        # Set PyAutoGUI settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.config.click_interval

    def clear_console(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def setup_logging(self):
        """Configure logging to file only"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='dialogue_skipper.log',
            filemode='a'
        )

    def load_config(self) -> Config:
        """Load configuration from file or create default"""
        config_file = 'dialogue_skipper_config.json'
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_dict = json.load(f)
                    config = Config(**config_dict)
                    return config
            except Exception as e:
                logging.warning(f"Could not load config file: {e}")
        
        # Create default config and save it
        config = Config()
        self.save_config(config)
        return config

    def save_config(self, config: Config):
        """Save configuration to file"""
        try:
            with open('dialogue_skipper_config.json', 'w') as f:
                json.dump(asdict(config), f, indent=4)
        except Exception as e:
            logging.error(f"Could not save config file: {e}")
            print(f"{Fore.RED}Warning: Could not save configuration file.")

    def is_admin(self) -> bool:
        """Check if running with admin privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            logging.error(f"Failed to check admin status: {e}")
            return False

    def run_as_admin(self):
        """Relaunch script with admin privileges if needed"""
        if not self.is_admin():
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, 
                    " ".join([f'"{arg}"' for arg in sys.argv]), 
                    None, 1
                )
                logging.info("Relaunched script with admin privileges")
                sys.exit()
            except Exception as e:
                logging.error(f"Failed to relaunch as admin: {e}")
                print(f"{Fore.RED}Error: Could not run as administrator. Please run manually with admin privileges.")
                input(f"{Fore.YELLOW}Press Enter to continue anyway...")

    def select_resolution(self) -> Tuple[int, int]:
        """Interactive resolution selection with custom option"""
        self.clear_console()
        self.print_banner()
        
        resolutions = {
            "1": {"res": "1280x720 (HD)", "x": 960, "y": 540},
            "2": {"res": "1366x768", "x": 1024, "y": 576},
            "3": {"res": "1600x900 (HD+)", "x": 1200, "y": 675},
            "4": {"res": "1920x1080 (Full HD)", "x": 1350, "y": 750},
            "5": {"res": "2560x1440 (QHD)", "x": 1920, "y": 1080},
            "6": {"res": "3840x2160 (4K UHD)", "x": 2700, "y": 1500},
            "7": {"res": "Custom Coordinates", "x": None, "y": None},
            "8": {"res": "Current Configuration", "x": self.config.click_x, "y": self.config.click_y}
        }
        
        print(f"\n{Fore.CYAN}═══ Select Click Position ═══")
        for key, value in resolutions.items():
            if key == "8":
                print(f"{Fore.YELLOW}{key}: {value['res']} {Fore.GREEN}({value['x']}, {value['y']})")
            elif key == "7":
                print(f"{Fore.YELLOW}{key}: {value['res']}")
            else:
                print(f"{Fore.YELLOW}{key}: {value['res']} {Fore.CYAN}→ ({value['x']}, {value['y']})")
        
        while True:
            choice = input(f"\n{Fore.CYAN}Enter choice (1-8): {Style.RESET_ALL}")
            if choice in resolutions:
                break
            print(f"{Fore.RED}Invalid choice. Please select 1-8.")
        
        if choice == "7":
            try:
                print(f"\n{Fore.CYAN}Custom Coordinates Setup:")
                x = int(input(f"Enter X coordinate: {Style.RESET_ALL}"))
                y = int(input(f"Enter Y coordinate: {Style.RESET_ALL}"))
                
                # Validate coordinates
                screen_width, screen_height = pyautogui.size()
                if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                    print(f"{Fore.YELLOW}Warning: Coordinates may be outside screen bounds ({screen_width}x{screen_height})")
                    if input(f"Continue anyway? (y/n): ").lower() != 'y':
                        return self.config.click_x, self.config.click_y
                
                # Save to config for future use
                self.config.click_x = x
                self.config.click_y = y
                self.save_config(self.config)
                
                print(f"{Fore.GREEN}✓ Custom coordinates saved: ({x}, {y})")
                logging.info(f"Selected custom resolution with coordinates ({x}, {y})")
                input(f"\n{Fore.CYAN}Press Enter to continue...")
                return x, y
            except ValueError as e:
                logging.error(f"Invalid coordinate input: {e}")
                print(f"{Fore.RED}Error: Invalid coordinates. Using current config.")
                input(f"{Fore.YELLOW}Press Enter to continue...")
                return self.config.click_x, self.config.click_y
        else:
            x, y = resolutions[choice]["x"], resolutions[choice]["y"]
            
            # Update config if not using current
            if choice != "8":
                self.config.click_x = x
                self.config.click_y = y
                self.save_config(self.config)
                print(f"\n{Fore.GREEN}✓ Position saved: {resolutions[choice]['res']} → ({x}, {y})")
            else:
                print(f"\n{Fore.GREEN}✓ Using current position: ({x}, {y})")
            
            logging.info(f"Selected resolution {resolutions[choice]['res']} with coordinates ({x}, {y})")
            input(f"\n{Fore.CYAN}Press Enter to continue...")
            return x, y

    def configure_settings(self):
        """Interactive settings configuration with improved UI"""
        self.clear_console()
        self.print_banner()
        
        print(f"\n{Fore.CYAN}═══ Advanced Configuration ═══")
        
        # Hotkey configuration
        print(f"\n{Fore.YELLOW}📋 Current Hotkeys:")
        print(f"   Start/Stop: {Fore.GREEN}{self.config.start_stop_key.upper()}")
        print(f"   Pause/Resume: {Fore.GREEN}{self.config.pause_key.upper()}")
        print(f"   Emergency Stop: {Fore.GREEN}{self.config.emergency_stop_key.upper()}")
        
        if input(f"\n{Fore.CYAN}Modify hotkeys? (y/n): ").lower() == 'y':
            print(f"\n{Fore.CYAN}Hotkey Configuration:")
            try:
                new_start = input(f"Start/Stop key (current: {self.config.start_stop_key}): ").strip()
                if new_start:
                    self.config.start_stop_key = new_start.lower()
                
                new_pause = input(f"Pause/Resume key (current: {self.config.pause_key}): ").strip()
                if new_pause:
                    self.config.pause_key = new_pause.lower()
                
                new_emergency = input(f"Emergency Stop key (current: {self.config.emergency_stop_key}): ").strip()
                if new_emergency:
                    self.config.emergency_stop_key = new_emergency.lower()
                
                print(f"{Fore.GREEN}✓ Hotkeys updated successfully!")
            except Exception as e:
                print(f"{Fore.RED}Error configuring hotkeys: {e}")
        
        # Click timing settings
        print(f"\n{Fore.YELLOW}⚡ Click Performance:")
        print(f"   Click Interval: {Fore.GREEN}{self.config.click_interval}s {Fore.CYAN}({1/self.config.click_interval:.0f} clicks/sec)")
        print(f"   Auto-stop Timer: {Fore.GREEN}{self.config.auto_stop_time}s {Fore.CYAN}({self.config.auto_stop_time//60}m {self.config.auto_stop_time%60}s)")
        
        if input(f"\n{Fore.CYAN}Modify timing settings? (y/n): ").lower() == 'y':
            print(f"\n{Fore.CYAN}Performance Configuration:")
            try:
                interval = input(f"Click interval in seconds (current: {self.config.click_interval}): ").strip()
                if interval:
                    new_interval = float(interval)
                    if 0.001 <= new_interval <= 10:
                        self.config.click_interval = new_interval
                        print(f"{Fore.GREEN}✓ Click speed: {1/new_interval:.0f} clicks/second")
                    else:
                        print(f"{Fore.YELLOW}Warning: Interval should be between 0.001 and 10 seconds")
                
                auto_stop = input(f"Auto-stop time in seconds (current: {self.config.auto_stop_time}): ").strip()
                if auto_stop:
                    new_time = int(auto_stop)
                    if 1 <= new_time <= 7200:  # Max 2 hours
                        self.config.auto_stop_time = new_time
                        print(f"{Fore.GREEN}✓ Auto-stop: {new_time//60}m {new_time%60}s")
                    else:
                        print(f"{Fore.YELLOW}Warning: Auto-stop should be between 1 and 7200 seconds")
                
            except ValueError as e:
                print(f"{Fore.RED}Invalid input: {e}")
        
        # Display settings
        print(f"\n{Fore.YELLOW}🖥️ Display Options:")
        print(f"   Click Counter: {Fore.GREEN if self.config.show_click_counter else Fore.RED}{'ON' if self.config.show_click_counter else 'OFF'}")
        print(f"   Elapsed Timer: {Fore.GREEN if self.config.show_elapsed_time else Fore.RED}{'ON' if self.config.show_elapsed_time else 'OFF'}")
        
        if input(f"\n{Fore.CYAN}Modify display settings? (y/n): ").lower() == 'y':
            print(f"\n{Fore.CYAN}Display Configuration:")
            counter = input(f"Show click counter? (y/n): ").strip().lower()
            if counter in ['y', 'n']:
                self.config.show_click_counter = counter == 'y'
                print(f"{Fore.GREEN}✓ Click counter: {'ON' if self.config.show_click_counter else 'OFF'}")
            
            timer = input(f"Show elapsed time? (y/n): ").strip().lower()
            if timer in ['y', 'n']:
                self.config.show_elapsed_time = timer == 'y'
                print(f"{Fore.GREEN}✓ Timer display: {'ON' if self.config.show_elapsed_time else 'OFF'}")
        
        # Save configuration
        self.save_config(self.config)
        print(f"\n{Fore.GREEN}✓ All settings saved successfully!")
        input(f"\n{Fore.CYAN}Press Enter to continue...")

    def update_status_display(self):
        """Update the status display with current information and improved formatting"""
        with self.status_lock:
            status_parts = []
            
            # Main status with colored indicators
            if self.is_active:
                if self.is_paused:
                    status_parts.append(f"{Fore.YELLOW}⏸️  PAUSED")
                else:
                    status_parts.append(f"{Fore.GREEN}▶️  ACTIVE")
            else:
                status_parts.append(f"{Fore.MAGENTA}⏹️  READY")
            
            # Click counter with rate
            if self.config.show_click_counter and self.is_active:
                elapsed = time.time() - self.start_time if self.start_time > 0 else 1
                rate = self.click_count / elapsed if elapsed > 0 else 0
                status_parts.append(f"{Fore.CYAN}Clicks: {self.click_count} ({rate:.1f}/s)")
            
            # Enhanced time display
            if self.config.show_elapsed_time and self.is_active and self.start_time > 0:
                elapsed = time.time() - self.start_time
                remaining = max(0, self.config.auto_stop_time - elapsed)
                
                # Format time nicely
                elapsed_str = f"{elapsed:.1f}s" if elapsed < 60 else f"{int(elapsed//60)}m{int(elapsed%60):02d}s"
                total_str = f"{self.config.auto_stop_time}s" if self.config.auto_stop_time < 60 else f"{int(self.config.auto_stop_time//60)}m{int(self.config.auto_stop_time%60):02d}s"
                
                status_parts.append(f"{Fore.BLUE}Time: {elapsed_str}/{total_str}")
                
                if remaining < 30:
                    remaining_str = f"{remaining:.1f}s" if remaining < 60 else f"{int(remaining//60)}m{int(remaining%60):02d}s"
                    status_parts.append(f"{Fore.RED}⏰ {remaining_str} left")
            
            # Current coordinates
            status_parts.append(f"{Fore.MAGENTA}@({self.config.click_x},{self.config.click_y})")
            
            # Create a clean status line
            status_line = " │ ".join(status_parts)
            terminal_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 120
            padding = max(0, terminal_width - len(status_line) - 20)
            
            sys.stdout.write(f"\r{status_line}{' ' * padding}")
            sys.stdout.flush()

    def click_loop(self, x: int, y: int):
        """Main clicking loop with pause support and enhanced feedback"""
        self.click_count = 0
        self.start_time = time.time()
        
        print(f"\n{Fore.GREEN}🚀 Clicking started at ({x}, {y})")
        print(f"{Fore.CYAN}Press {self.config.pause_key.upper()} to pause, {self.config.emergency_stop_key.upper()} for emergency stop\n")
        
        last_update = 0
        
        while not self.stop_event.is_set():
            current_time = time.time()
            
            # Check if we should auto-stop
            if current_time - self.start_time >= self.config.auto_stop_time:
                print(f"\n{Fore.YELLOW}⏰ Auto-stop timer reached ({self.config.auto_stop_time}s)")
                break
            
            # Handle pause
            if self.pause_event.is_set():
                time.sleep(0.1)
                if current_time - last_update > 1:  # Update display every second while paused
                    self.update_status_display()
                    last_update = current_time
                continue
            
            try:
                pyautogui.click(x, y)
                self.click_count += 1
                
                # Update display more frequently for better UX
                if current_time - last_update > 0.5:  # Update every 0.5 seconds
                    self.update_status_display()
                    last_update = current_time
                
                time.sleep(self.config.click_interval)
                
            except pyautogui.FailSafeException:
                print(f"\n{Fore.YELLOW}🛑 Mouse failsafe activated - moved to screen corner")
                logging.info("FailSafe triggered - mouse moved to corner")
                break
            except Exception as e:
                logging.error(f"Error in click loop: {e}")
                print(f"\n{Fore.RED}Error in clicking: {e}")
                break
        
        # Calculate final statistics
        total_time = time.time() - self.start_time
        avg_rate = self.click_count / total_time if total_time > 0 else 0
        
        # Reset state
        self.is_active = False
        self.is_paused = False
        self.stop_event.set()
        self.pause_event.clear()
        
        # Show completion summary
        print(f"\n{Fore.GREEN}✅ Session Complete!")
        print(f"{Fore.CYAN}Total Clicks: {Fore.YELLOW}{self.click_count}")
        print(f"{Fore.CYAN}Duration: {Fore.YELLOW}{total_time:.1f}s")
        print(f"{Fore.CYAN}Average Rate: {Fore.YELLOW}{avg_rate:.1f} clicks/second")
        
        logging.info(f"Click session completed - Clicks: {self.click_count}, Duration: {total_time:.1f}s, Rate: {avg_rate:.1f}/s")
        self.update_status_display()

    def setup_hotkeys(self):
        """Setup all hotkeys with error handling"""
        def on_start_stop(e):
            if not self.is_active:
                # Start clicking
                self.stop_event.clear()
                self.pause_event.clear()
                self.is_active = True
                self.is_paused = False
                
                self.click_thread = threading.Thread(
                    target=self.click_loop, 
                    args=(self.config.click_x, self.config.click_y),
                    daemon=True
                )
                self.click_thread.start()
                
                logging.info("Script started")
                self.update_status_display()
            else:
                # Stop clicking
                self.stop_event.set()
                self.is_active = False
                self.is_paused = False
                
                if self.click_thread:
                    self.click_thread.join(timeout=1.0)
                
                logging.info("Script stopped by hotkey")
                self.update_status_display()

        def on_pause(e):
            if self.is_active:
                self.is_paused = not self.is_paused
                if self.is_paused:
                    self.pause_event.set()
                    print(f"\n{Fore.YELLOW}⏸️  Paused")
                    logging.info("Script paused")
                else:
                    self.pause_event.clear()
                    print(f"\n{Fore.GREEN}▶️  Resumed")
                    logging.info("Script resumed")
                self.update_status_display()

        def on_emergency_stop(e):
            if self.is_active:
                self.stop_event.set()
                self.is_active = False
                self.is_paused = False
                if self.click_thread:
                    self.click_thread.join(timeout=1.0)
                logging.info("Emergency stop activated")
                print(f"\n{Fore.RED}🚨 EMERGENCY STOP ACTIVATED! 🚨{Style.RESET_ALL}")
                self.update_status_display()

        # Register hotkeys with improved error handling
        hotkey_configs = [
            (self.config.start_stop_key, on_start_stop, "Start/Stop"),
            (self.config.pause_key, on_pause, "Pause/Resume"),
            (self.config.emergency_stop_key, on_emergency_stop, "Emergency Stop")
        ]
        
        registered_count = 0
        failed_keys = []
        
        for key, handler, description in hotkey_configs:
            try:
                keyboard.on_press_key(key, handler)
                registered_count += 1
            except Exception as e:
                logging.error(f"Error registering {description} hotkey ({key}): {e}")
                failed_keys.append(f"{description} ({key})")
        
        if registered_count == len(hotkey_configs):
            print(f"{Fore.GREEN}✓ All hotkeys registered successfully!")
        else:
            print(f"{Fore.YELLOW}⚠️  {registered_count}/{len(hotkey_configs)} hotkeys registered")
            if failed_keys:
                print(f"{Fore.RED}Failed: {', '.join(failed_keys)}")

    def print_banner(self):
        """Print application banner with improved styling"""
        print(f"{Back.BLUE}{Fore.WHITE}")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 8 + "HONKAI STAR RAIL DIALOGUE SKIPPER" + " " * 17 + "║")
        print("╚" + "═" * 58 + "╝")
        print(f"{Style.RESET_ALL}")

    def show_current_config(self):
        """Display current configuration with improved formatting"""
        self.clear_console()
        self.print_banner()
        
        print(f"\n{Fore.CYAN}═══ Current Configuration ═══")
        
        # Hotkeys section
        print(f"\n{Fore.YELLOW}🎮 Hotkeys:")
        print(f"   Start/Stop: {Fore.GREEN}{self.config.start_stop_key.upper()}")
        print(f"   Pause/Resume: {Fore.GREEN}{self.config.pause_key.upper()}")
        print(f"   Emergency Stop: {Fore.GREEN}{self.config.emergency_stop_key.upper()}")
        
        # Click settings
        print(f"\n{Fore.YELLOW}⚡ Performance:")
        print(f"   Click Position: {Fore.GREEN}({self.config.click_x}, {self.config.click_y})")
        print(f"   Click Speed: {Fore.GREEN}{1/self.config.click_interval:.0f} clicks/second {Fore.CYAN}({self.config.click_interval}s interval)")
        print(f"   Auto-stop Timer: {Fore.GREEN}{self.config.auto_stop_time//60}m {self.config.auto_stop_time%60}s {Fore.CYAN}({self.config.auto_stop_time}s total)")
        
        # UI settings
        print(f"\n{Fore.YELLOW}🖥️  Display:")
        print(f"   Click Counter: {Fore.GREEN if self.config.show_click_counter else Fore.RED}{'ON' if self.config.show_click_counter else 'OFF'}")
        print(f"   Timer Display: {Fore.GREEN if self.config.show_elapsed_time else Fore.RED}{'ON' if self.config.show_elapsed_time else 'OFF'}")
        
        # Screen info
        try:
            screen_width, screen_height = pyautogui.size()
            print(f"\n{Fore.YELLOW}📱 Screen Info:")
            print(f"   Resolution: {Fore.GREEN}{screen_width}x{screen_height}")
            print(f"   Click Valid: {Fore.GREEN if 0 <= self.config.click_x <= screen_width and 0 <= self.config.click_y <= screen_height else Fore.RED}{'YES' if 0 <= self.config.click_x <= screen_width and 0 <= self.config.click_y <= screen_height else 'NO'}")
        except Exception as e:
            print(f"\n{Fore.RED}Could not detect screen info: {e}")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...")

    def main_menu(self):
        """Display main menu and handle user choices with improved UI"""
        while True:
            self.clear_console()
            self.print_banner()
            
            print(f"\n{Fore.CYAN}═══ Main Menu ═══")
            print(f"{Fore.GREEN}1. {Fore.WHITE}🚀 Start Dialogue Skipper")
            print(f"{Fore.YELLOW}2. {Fore.WHITE}🎯 Configure Click Position")
            print(f"{Fore.YELLOW}3. {Fore.WHITE}⚙️  Advanced Settings")
            print(f"{Fore.CYAN}4. {Fore.WHITE}📋 View Current Configuration")
            print(f"{Fore.RED}5. {Fore.WHITE}❌ Exit Program")
            
            # Show quick status
            print(f"\n{Fore.MAGENTA}Current Position: {Fore.CYAN}({self.config.click_x}, {self.config.click_y}) {Fore.YELLOW}@ {1/self.config.click_interval:.0f} clicks/sec")
            
            choice = input(f"\n{Fore.CYAN}Select option (1-5): {Style.RESET_ALL}").strip()
            
            if choice == "1":
                self.clear_console()
                break
            elif choice == "2":
                x, y = self.select_resolution()
                self.config.click_x = x
                self.config.click_y = y
                self.save_config(self.config)
            elif choice == "3":
                self.configure_settings()
            elif choice == "4":
                self.show_current_config()
            elif choice == "5":
                self.clear_console()
                print(f"{Fore.GREEN}Thank you for using Dialogue Skipper!")
                print(f"{Fore.CYAN}Stay safe and enjoy your gaming! 🎮")
                sys.exit(0)
            else:
                print(f"{Fore.RED}❌ Invalid choice. Please select 1-5.")
                time.sleep(1.5)

    def run(self):
        """Main application entry point with enhanced error handling"""
        try:
            # Initial setup
            self.run_as_admin()
            
            # Main menu and configuration
            self.main_menu()
            
            # Start the application
            self.print_banner()
            print(f"\n{Fore.GREEN}🎮 Dialogue Skipper Ready!")
            print(f"{Fore.CYAN}Click Position: {Fore.YELLOW}({self.config.click_x}, {self.config.click_y})")
            print(f"{Fore.CYAN}Click Speed: {Fore.YELLOW}{1/self.config.click_interval:.0f} clicks/second")
            print(f"{Fore.CYAN}Auto-stop: {Fore.YELLOW}{self.config.auto_stop_time//60}m {self.config.auto_stop_time%60}s")
            
            print(f"\n{Fore.YELLOW}🎮 Controls:")
            print(f"   {Fore.GREEN}{self.config.start_stop_key.upper()}{Fore.WHITE} - Start/Stop clicking")
            print(f"   {Fore.GREEN}{self.config.pause_key.upper()}{Fore.WHITE} - Pause/Resume")
            print(f"   {Fore.GREEN}{self.config.emergency_stop_key.upper()}{Fore.WHITE} - Emergency stop")
            print(f"   {Fore.GREEN}CTRL+C{Fore.WHITE} - Exit program")
            
            print(f"\n{Fore.RED}⚠️  Safety: Move mouse to screen corner for emergency stop")
            print(f"{Fore.MAGENTA}Ready! Press {self.config.start_stop_key.upper()} when in-game...")
            
            self.setup_hotkeys()
            self.update_status_display()
            
            # Keep the script running
            keyboard.wait()
            
        except KeyboardInterrupt:
            self.stop_event.set()
            if self.click_thread and self.click_thread.is_alive():
                print(f"\n{Fore.YELLOW}Stopping click thread...")
                self.click_thread.join(timeout=2.0)
            
            self.clear_console()
            print(f"\n{Fore.GREEN}✅ Dialogue Skipper closed safely")
            print(f"{Fore.CYAN}Thanks for using our tool! 🎮")
            logging.info("Script terminated by KeyboardInterrupt")
            
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            print(f"\n{Fore.RED}❌ An unexpected error occurred: {e}")
            print(f"{Fore.YELLOW}Check 'dialogue_skipper.log' for detailed error information.")
            input(f"\n{Fore.CYAN}Press Enter to exit...")

def main():
    """Application entry point with enhanced error handling"""
    try:
        skipper = DialogueSkipper()
        skipper.run()
    except Exception as e:
        print(f"{Fore.RED}Failed to initialize Dialogue Skipper: {e}")
        logging.error(f"Failed to initialize application: {e}")
        input(f"{Fore.YELLOW}Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()