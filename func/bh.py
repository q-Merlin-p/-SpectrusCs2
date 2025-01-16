import pymem
import pymem.process
import time
import os
import ctypes
import json
from requests import get
from PySide6.QtCore import QFileSystemWatcher, QCoreApplication
import threading

class Utility:
    """Contains utility functions for the application."""
    @staticmethod
    def fetch_offsets():
        """Fetches offsets from the GitHub repository."""
        try:
            response = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/buttons.hpp")
            if response.status_code == 200:
                offsets = response.text
                # Extract dwForceJump offset from the line containing "jump"
                for line in offsets.splitlines():
                    if "jump" in line:
                        # Extract the offset value after the last '=' symbol, and remove any trailing characters
                        offset_str = line.split('=')[-1].strip().rstrip(';')
                        offset = int(offset_str, 16)
                        return offset
            else:
                print(f"Failed to fetch offsets from server.")
        except Exception as e:
            print(f"Failed to fetch offsets: {e}")
        return None


def load_settings():
    config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
    config_path = os.path.join(config_dir, "config.json")

    default_settings = { "bunnyHopActivity": 0}
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                settings = json.load(f)
                return settings
        except json.JSONDecodeError:
            pass 
    return default_settings

class Bhop:
    def __init__(self, settings):
        """Initializes the Bhop instance."""
        self.settings = settings 
        self.pm = None
        self.dwForceJump = Utility.fetch_offsets()
        self.client_base = None
        self.force_jump_address = None

    def initialize_pymem(self):
        """Initializes Pymem and attaches to the game process."""
        try:
            self.pm = pymem.Pymem("cs2.exe")
        except pymem.exception.ProcessNotFound:
            print(f"Could not find cs2.exe process. Please make sure the game is running.")
            return False
        except pymem.exception.PymemError as e:
            print(f"encountered an error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during Pymem initialization: {e}")
            return False
        return True 

    def get_client_module(self):
        """Retrieves the base address of the client.dll module."""
        try:
            if self.client_base is None:
                client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
                if not client_module:
                    raise pymem.exception.ModuleNotFoundError("client.dll not found")
                self.client_base = client_module.lpBaseOfDll
                self.force_jump_address = self.client_base + self.dwForceJump  
        except pymem.exception.ModuleNotFoundError as e:
            print(f"Error: {e}. Ensure client.dll is loaded.")
            return False
        except Exception as e:
            print(f"Unexpected error retrieving client module: {e}")
            return False
        return True                         

    def start(self):
        """Starts the bunnyhop loop."""
        jump = False
        while True:
            try:
                if self.settings.get('bunnyHopActivity') == 1:
                    if not self.initialize_pymem():
                        input(f"Press Enter to exit...")
                        return

                    if not self.get_client_module():
                        input(f"Press Enter to exit...")
                        return

                    # Bunny hop logic
                    if ctypes.windll.user32.GetAsyncKeyState(0x20): 
                        if not jump:
                            time.sleep(0.01)
                            self.pm.write_int(self.force_jump_address, 65537)
                            jump = True
                        else:
                            time.sleep(0.01)
                            self.pm.write_int(self.force_jump_address, 256)
                            jump = False
                else:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Unexpected error: {e}")
                input(f"Press Enter to exit...")

    def reload_settings(self):
        """Reloads settings when the configuration file changes."""
        new_settings = load_settings()
        self.settings.update(new_settings)

def monitor_config_changes(bhop):
    config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
    config_path = os.path.join(config_dir, "config.json")

    app = QCoreApplication([]) 

    watcher = QFileSystemWatcher()
    watcher.addPath(config_path)

    def on_file_changed():
        bhop.reload_settings() 

    watcher.fileChanged.connect(on_file_changed)
    app.exec()  

def starter():
    print("Bhop process started.")
    settings = load_settings() 
    bhop = Bhop(settings)  
    threading.Thread(target=monitor_config_changes, args=(bhop,), daemon=True).start()
    bhop.start()

