import os

from cryptography.fernet import Fernet
from utilities.key_manager import load_key

def decrypt_message(encrypted_message):
    key_file_path = os.path.join(os.path.dirname(__file__), "secret.key")
    key = load_key(key_file_path)
    cipher = Fernet(key)
    encoded_encrypted_message = encrypted_message.encode('')
    decrypted_message = cipher.decrypt(encoded_encrypted_message)
    return decrypted_message
