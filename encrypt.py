from hashlib import sha256
import os, base64, subprocess, sys, random, string, re #  Please be on a linux system and have wl-copy and xclip installed
try:
    from Crypto.Cipher import AES # Please make sure the python-pycryptodome package is installed
    from Crypto.Util.Padding import pad, unpad
except ModuleNotFoundError: # Check if pycryptodome is installed
    print("Please install python-pycryptodome")
    sys.exit(1) # Exit with an error
import os, base64, subprocess, sys, random, string #  Please be on a linux system and have wl-copy and xclip installed
key_file_path = "/tmp/key" # This is designed to store in the ram on a linux system. This path can be changed.
def copy_to_clipboard(text): # This copies text to the clipboard for the specific desktop environment
    subprocess.run(["wl-copy"], input=text.encode()) if os.environ.get("XDG_SESSION_TYPE") == "wayland" else subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode())
if (len(sys.argv) > 1): # This checks for a flag
    if sys.argv[1] == "-n": # If flag is -n, delete the key file to manually change key
        os.remove(key_file_path) if os.path.exists(key_file_path) else None
    elif sys.argv[1] == "-p": # If flag is -p, create a new random password
        password = ("@@"+''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=30))) # Create new password by splicing strings together
        copy_to_clipboard(password) # Copy new password to clipboard. k on previous line is length of random password
        with open(key_file_path, 'w') as key_file: key_file.write(password) # Overwrite the filepath with the new password
        print(f"New password saved to {key_file_path} and copied to clipboard.")
        sys.exit(0) # Finish script and indicate success
clipboard_content = subprocess.getoutput("wl-paste" if os.environ.get("XDG_SESSION_TYPE") == "wayland" else "xclip -o -selection clipboard")
def password_logic(): # Above line sets a varaible to the text on the clipboard before running the script
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
    except (ValueError, KeyError): # This detects if it is unable to decrypt the code with the password
        return None
def process_clipboard_content(content, password, copy=False):
    if "&&" in content: # This detects if the text on the clipboard is encrypted and knows to decrypt it
        content = re.sub(r"@[^&]*(?=&&)|@.*$", "", content).replace(" ", "") # Remove if u triple clicked with included ping (i hate regex)
        content = re.sub(r"<.*?>", "", content) # Remove pings if u used built in copy button
        print("Decrypted text:", decrypt(content[2:], password) or "Incorrect password.")
        if copy: copy_to_clipboard("")
    else:
        encrypted_text = "&&" + encrypt(input("Text Input: "), password) # This encrypts text and makes it start with "&&"
        (copy_to_clipboard(encrypted_text), print("Encrypted text copied to clipboard.")) if copy else print(encrypted_text)
password = password_logic() # This runs the code to check if the password exists and set it
process_clipboard_content(clipboard_content, password, copy=True) # This runs the main process
