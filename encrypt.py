from hashlib import sha256
from Crypto.Cipher import AES # Please make sure the pycryptodome package is installed
from Crypto.Util.Padding import pad, unpad
import os, base64, subprocess, sys # Please be on a linux system and have wl-copy and xclip installed
key_file_path = "/tmp/key" # this is designed to store in the ram on a linux system.
clipboard_content = subprocess.getoutput("wl-paste" if os.environ.get("XDG_SESSION_TYPE") == "wayland"
else "xclip -o -selection clipboard") # This sets a varaible to the text on the clipboard before run
def password_logic():
    if clipboard_content.startswith("@@"): # This checks if the text on the clipboard starts with "@@"
        with open(key_file_path, 'w') as key_file: key_file.write(clipboard_content)
        print(f"New password pasted to {key_file_path}") # And if it does, it makes the new key be whats on the clipboard
    if os.path.exists(key_file_path):
        with open(key_file_path, 'r') as key_file: return key_file.read()
    password = input("Password to store until next reboot: ") # This manually takes the password if need be
    with open(key_file_path, 'w') as key_file: key_file.write(password)
    print(f"Password saved to {key_file_path}.")
    return password
def encrypt(plaintext, passphrase): # This encrypts the text with AES according to the password specified
    key, iv = sha256(passphrase.encode()).digest(), os.urandom(AES.block_size)
    ciphertext = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()
def decrypt(ciphertext, passphrase): # This attempts to decrypt the text according to the password
    try:
        key, decoded_data = sha256(passphrase.encode()).digest(), base64.b64decode(ciphertext)
        cipher = AES.new(key, AES.MODE_CBC, decoded_data[:AES.block_size])
        return unpad(cipher.decrypt(decoded_data[AES.block_size:]), AES.block_size).decode()
    except (ValueError, KeyError): # This detects if it is unable to decrypt the text with the password
        return None
def copy_to_clipboard(text): # This copies text to the clipboard for the specific desktop environment
    subprocess.run(["wl-copy"], input=text.encode()) if os.environ.get("XDG_SESSION_TYPE") == "wayland"
    else subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode())
def process_clipboard_content(content, password, copy=False):
    if content.startswith("&&"): # This detects if the text on the clipboard is encrypted and knows to decrypt it
        print("Decrypted text:", decrypt(content[2:], password) or "Incorrect password.")
        if copy: copy_to_clipboard("")
    else:
        encrypted_text = "&&" + encrypt(input("Text Input: "), password) # This encrypts text and makes it start with "&&"
        (copy_to_clipboard(encrypted_text), print("Encrypted text copied to clipboard.")) if copy else print(encrypted_text)
if (len(sys.argv) > 1 and sys.argv[1] == "-n"): # This checks for a flag to manually change the password
    os.remove(key_file_path) if os.path.exists(key_file_path) else None
password = password_logic() # This runs the code to check if the password exists and set it
process_clipboard_content(clipboard_content, password, copy=True) # This runs the main process
