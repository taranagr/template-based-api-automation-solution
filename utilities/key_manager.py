from cryptography.fernet import Fernet

def load_key(file_path):
    with open(file_path,'rb') as key_file:
        key = key_file.read()
    return key

def generate_key(file_path):
    key = Fernet.generate_key()
    with open(file_path,'wb') as key_file:
        key_file.write(key)
    return key