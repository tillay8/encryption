import os, subprocess, sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def get_clipboard_tool():
    return ["wl-copy"] if os.environ.get("XDG_SESSION_TYPE") == "wayland" else ["xclip", "-selection", "clipboard"]

def clipboard_content():
    try:
        return subprocess.run(get_clipboard_tool() + ["-o"], capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        print("Error reading clipboard. Install xclip or wl-copy.")
        return None

def write_to_clipboard(data):
    try:
        subprocess.run(get_clipboard_tool(), input=data.encode(), check=True)
    except subprocess.CalledProcessError:
        print("Failed to write to clipboard. Install xclip or wl-copy.")

def generate_keypair():
    try:
        key = RSA.generate(2048)
        name = input("Enter name for key pair: ").strip()
        with open(f"{name}_private.key", "wb") as priv_file, open(f"{name}_public.key", "wb") as pub_file:
            priv_file.write(key.export_key())
            pub_file.write(key.publickey().export_key())
        print(f"New keypair: {name}_private.key and {name}_public.key")
    except Exception as e:
        print(f"Error generating keypair: {e}")

def encrypt_message():
    public_keys = [f.replace('_public.key', '') for f in os.listdir() if f.endswith("_public.key")]
    if not public_keys:
        print("No public keys found. Try making friends first.")
        return

    clipboard = clipboard_content()
    message = clipboard if clipboard and clipboard.startswith("@@") else input("Message to encrypt: ")
    if clipboard and clipboard.startswith("@@"):
        print("Password detected in clipboard. Encrypting automatically.")
    recipients = []
    print(f"Choose recipient(s) {public_keys} (q to finish): ")
    while (pub_key_name := input("> ")) != 'q':
        if pub_key_name in public_keys:
            recipients.append(pub_key_name)
        else:
            print(f"Who is {pub_key_name} lol. ignoring")

    encrypted_msgs = [
        PKCS1_OAEP.new(RSA.import_key(open(f"{key}_public.key", "rb").read())).encrypt(message.encode()).hex()
        for key in recipients
    ]

    priv_key_name = input("Private key to sign with: ").strip()
    if priv_key_name not in private_keys:
        print(f"rivate key: {priv_key_name}")
    signature = pkcs1_15.new(RSA.import_key(open(f"{priv_key_name}_private.key", "rb").read())).sign(SHA256.new(message.encode()))
    encrypted_data = "$$".join(encrypted_msgs) + f"||{signature.hex()}"
    write_to_clipboard(encrypted_data)
    print("Encrypted message copied to clipboard.")

def decrypt_message():
    encrypted_data = clipboard_content()
    if not encrypted_data:
        print("Clipboard empty or unreadable.")
    if not private_keys:
        print("No private keys available. Generate a keypair first.")
    try:
        priv_key_name = input(f"Choose private key {private_keys}: ").strip()
        if priv_key_name not in private_keys:
            print(f"Unknown private key: {priv_key_name}")
        private_key = RSA.import_key(open(f"{priv_key_name}_private.key", "rb").read())
        encrypted_msgs, signature = encrypted_data.split("||")[0].split("$$"), bytes.fromhex(encrypted_data.split("||")[-1])
        for encrypted_msg in encrypted_msgs:
            try:
                decrypted_message = PKCS1_OAEP.new(private_key).decrypt(bytes.fromhex(encrypted_msg)).decode()
                break
            except ValueError:
                continue
        else:
            print("Decryption failed. Invalid keys or data.")
        if decrypted_message.startswith("@@"):
            write_to_clipboard(decrypted_message)
            print("Password detected and copied to clipboard.")
        sender_pub_key_name = input("Sender's public key name: ").strip()
        sender_public_key = RSA.import_key(open(f"{sender_pub_key_name}_public.key", "rb").read())
        try:
            pkcs1_15.new(sender_public_key).verify(SHA256.new(decrypted_message.encode()), signature)
            print(f"Decrypted message: {decrypted_message}")
        except (ValueError, TypeError):
            print("Incorrect sender chosen.")
    except Exception as e:
        print(f"Decryption error: {e}")

private_keys = [f.replace('_private.key', '') for f in os.listdir() if f.endswith("_private.key")]
actions = {"1": generate_keypair, "2": encrypt_message, "3": decrypt_message}
print("1. Generate Key Pair\n2. Encrypt Message\n3. Decrypt Message")
actions.get(input("Choose action: "), lambda: print("Choose a valid number lol."))()
