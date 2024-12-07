from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os, base64, subprocess, sys
key_file_path = "/tmp/key"
def password_logic():
    if os.path.exists(key_file_path):
        with open(key_file_path, 'r') as key_file:
            password = key_file.read()
        return password
    else:
        password = input("Password to store until next reboot: ")
        with open(key_file_path, 'w') as key_file:
            key_file.write(password)
        print(f"Password saved to {key_file_path}.")
        return password
def encrypt(plaintext, passphrase):
    key, iv = sha256(passphrase.encode()).digest(), os.urandom(AES.block_size)
    ciphertext = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()
def decrypt(ciphertext, passphrase):
    try:
        key, decoded_data = sha256(passphrase.encode()).digest(), base64.b64decode(ciphertext)
        cipher = AES.new(key, AES.MODE_CBC, decoded_data[:AES.block_size])
        return unpad(cipher.decrypt(decoded_data[AES.block_size:]), AES.block_size).decode()
    except (ValueError, KeyError):
        return None
def copy_to_clipboard(text):
    try:
        if os.environ.get("XDG_SESSION_TYPE") == "wayland" and subprocess.check_output(["which", "wl-copy"]):
            subprocess.run(["wl-copy"], input=text.encode())
        elif os.environ.get("XDG_SESSION_TYPE") == "x11" and subprocess.check_output(["which", "xclip"]):
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode())
    except subprocess.CalledProcessError:
        print("Warning: Clipboard utility not found.")
def process_clipboard_content(content, password, copy=False):
    if content.startswith("&&"):
        decrypted_text = decrypt(content[2:], password)
        if decrypted_text is None:
            print("Incorrect password.")
        else:
            print(f"Decrypted text: {decrypted_text}")
        if copy:
            copy_to_clipboard("")
    else:
        encrypted_text = encrypt(input("Text Input: "), password)
        if copy:
            copy_to_clipboard("&&" + encrypted_text)
            print("Encrypted text copied to clipboard.")
        else:
            print("&&" + encrypted_text)

if (len(sys.argv) > 1 and sys.argv[1] == "-n"):
    os.remove(key_file_path) if os.path.exists(key_file_path) else None
password = password_logic()
try:
    clipboard_content = subprocess.getoutput("wl-paste" if os.environ.get("XDG_SESSION_TYPE") == "wayland" else "xclip -o -selection clipboard")
    if (clipboard_content.startswith("@@")):
        with open(key_file_path, 'w') as key_file:
            key_file.write(clipboard_content)
        print(f"new password pasted to {key_file_path}")
    process_clipboard_content(clipboard_content, password, copy=True)
except subprocess.CalledProcessError:
    print("Clipboard utility missing")
    clipboard_content = input("Input text manually: ")
    process_clipboard_content(clipboard_content, password)
