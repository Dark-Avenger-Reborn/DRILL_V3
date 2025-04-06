from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class encrypt_messages:
    def __init__(self):
        self.public_key = self.receive_public_key()
        self.private_key = self.receive_private_key()

    def encrypt(self, message):
        encrypted = public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    def decrypt(self, message):
        decrypted = private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode('utf-8')

    def read_file(self, file_name):
        try:
            with open(f"./encryption/{file_name}", "r") as file:
                result = file.readlines()
                file.close()
            return file
        except:
            raise Exception("File could not be read")

    def write_file(self, file_name, text):
        try:
            with open(f"./encryption/{file_name}", "w") as file:
                file.writelines(text)
                file.close()
        except:
            raise Exception("File could not be written to")

    def receive_private_key(self):
        try:
            private_pem = read_file("private_key.pem")
            return serialization.load_pem_private_key(private_pem, password=None)
        except:       
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            write_file("private_key.pem", private_pem)
            return private_key

    def receive_public_key(self):
        try:
            public_pem = read_file("public_key.pem")
            return serialization.load_pem_public_key(public_pem)
        except:       
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            write_file("public_key.pem", public_pem)
            return public_key