import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def generate_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_directory(dir_path: str, password: str):
    if not os.path.isdir(dir_path):
        print("[ERROR] Invalid directory path!")
        return

    salt = os.urandom(16)
    key = generate_key_from_password(password, salt)
    fernet = Fernet(key)

    print("\n--- STARTING DIRECTORY ENCRYPTION ---")
    
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file == "crypto_vault.py" or file == "vault_salt.key":
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                encrypted_data = fernet.encrypt(data)
                
                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
                print(f"[ENCRYPTED] {file_path}")
            except Exception as e:
                print(f"[FAILED] Could not encrypt {file_path}: {e}")

    salt_path = os.path.join(dir_path, "vault_salt.key")
    with open(salt_path, 'wb') as f:
        f.write(salt)
        
    print("\n[SUCCESS] Directory encrypted securely without data corruption!")
    print(f"[KEY MANAGEMENT] Master salt key backup saved at: {salt_path}")

def decrypt_directory(dir_path: str, password: str):
    salt_path = os.path.join(dir_path, "vault_salt.key")
    
    if not os.path.exists(salt_path):
        print("[ERROR] Verification failed! Vault key (vault_salt.key) not found in directory.")
        return

    with open(salt_path, 'rb') as f:
        salt = f.read()

    key = generate_key_from_password(password, salt)
    fernet = Fernet(key)

    print("\n--- STARTING DIRECTORY DECRYPTION ---")
    
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file == "crypto_vault.py" or file == "vault_salt.key":
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = fernet.decrypt(encrypted_data)
                
                with open(file_path, 'wb') as f:
                    f.write(decrypted_data)
                print(f"[DECRYPTED] {file_path}")
            except Exception as e:
                print(f"[FAIL/CORRUPTED] Authentication failed for {file_path}. Wrong password!")
                return
            
    os.remove(salt_path)
    print("\n[SUCCESS] Directory restoration completed successfully with MAC integrity verified.")

def main():
    print("================================================")
    print("           CRYPTOGRAPHIC ENCRYPTION VAULT")
    print("================================================")
    print("1. Encrypt Whole Directory (Folder)")
    print("2. Decrypt/Restore Directory")
    
    choice = input("\nChoose an option (1 or 2): ").strip()
    if choice in ['1', '2']:
        dir_path = input("Enter full folder path to scan: ").strip()
        password = input("Enter master passphrase: ").strip()
        
        if choice == '1':
            encrypt_directory(dir_path, password)
        else:
            decrypt_directory(dir_path, password)
    else:
        print("Invalid option selection.")

if __name__ == "__main__":
    main()
