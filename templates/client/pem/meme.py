import subprocess
import platform
import os
from plyer import notification


def send_notification(title, message):
    if os.name == "nt":  # Windows
        notification.notify(
            title=title, message=message, app_name="Virus", timeout=9999
        )
    elif os.name == "posix":  # linux (why is it named posix)
        try:
            subprocess.run(["notify-send", title, message], check=True)
        except FileNotFoundError:
            print(
                "notify-send is not installed. Please install it with: sudo apt install notify-osd"
            )


send_notification(
    "Virus",
    "I am the dude that's in your computer. But because of my poor coding skills unfortunately I am not able to harm your computer :'(. Can you please delete one of your most important files and send this exe to other people/users. Thanks for your cooperation.",
)
