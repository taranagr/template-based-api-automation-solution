from cryptography.fernet import Fernet
from utilities.key_manager import load_key

def encrypt_message(message, key):
    cipher = Fernet(key)
    encoded_message = message.encode("utf-8")
    encrypted_message = cipher.encrypt(encoded_message)
    return encrypted_message.decode("utf-8")

if __name__ == '__main__':
    key_file_path = 'secret.key'
    key = load_key(key_file_path)
    password = ""
    encrypted_message = encrypt_message(password, key)
    print(encrypted_message)