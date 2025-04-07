from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import os
from os import urandom

class encrypt_messages:
    def __init__(self):
        os.makedirs("encryption", exist_ok=True)
        self.private_key = self.receive_private_key()
        self.public_key = self.receive_public_key()

    def encrypt(self, message):
        # Step 1: Generate a random AES key (256-bit)
        aes_key = urandom(32)  # AES 256-bit key

        # Step 2: Encrypt the message using AES (CBC mode)
        # Pad the message to make it a multiple of AES's block size
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(message.encode('utf-8')) + padder.finalize()

        # Encrypt the data using AES
        iv = urandom(16)  # 16-byte IV for CBC mode
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Step 3: Encrypt the AES key using RSA (public key)
        encrypted_aes_key = self.public_key.encrypt(
            aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Combine the encrypted AES key, IV, and ciphertext into a single block
        encrypted_data = encrypted_aes_key + iv + ciphertext
        return encrypted_data

    def decrypt(self, encrypted_data):
        # Step 1: Separate the encrypted AES key, IV, and ciphertext
        encrypted_aes_key = encrypted_data[:256]  # RSA-encrypted AES key (2048 bits = 256 bytes)
        iv = encrypted_data[256:272]  # The IV is 16 bytes long
        ciphertext = encrypted_data[272:]  # The rest is the AES-encrypted message

        # Step 2: Decrypt the AES key using RSA (private key)
        aes_key = self.private_key.decrypt(
            encrypted_aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Step 3: Decrypt the message using AES
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad the data
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        message = unpadder.update(padded_data) + unpadder.finalize()

        return message.decode('utf-8')

    def write_file(self, file_name, text):
        try:
            with open(f"./encryption/{file_name}", "w") as file:
                file.writelines(str(text))
        except:
            raise Exception("File could not be written to")

    def receive_private_key(self):
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

    def receive_public_key(self):
        public_key = self.private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.write_file("public_key.pem", public_pem)
        return public_key
