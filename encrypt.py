import sys, subprocess, secrets, io, os, base64, random, string, binascii, re
from PIL import Image, UnidentifiedImageError
from hashlib import sha256
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
except ModuleNotFoundError:
    print("please install the cryptography package")
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ModuleNotFoundError:
    print("please install the pycryptodome package")
    sys.exit(1)
# Constants
PASSWORD_FILE = "/tmp/key"
prefix_text, prefix_password, prefix_image = "&&", "@@", "££"
message_file_path = os.path.expanduser("~/Downloads/message.txt")

# Clipboard functions
def copy_to_clipboard(data):
    cmd = ["wl-copy"] if os.environ.get("XDG_SESSION_TYPE") == "wayland" else ["xclip", "-selection", "clipboard"]
    subprocess.run(cmd, input=data.encode() if isinstance(data, str) else data)

def get_from_clipboard():
    cmd = ["wl-paste", "--no-newline"] if os.environ.get("XDG_SESSION_TYPE") == "wayland" else ["xclip", "-o", "-selection", "clipboard"]
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout

# Password handling
def password_logic():
    if clipboard_content.startswith(prefix_password.encode()):
        with open(PASSWORD_FILE, 'w') as f: f.write(clipboard_content.decode())
        print(f"New password saved to {PASSWORD_FILE}.")
        sys.exit(0)
    if os.path.exists(PASSWORD_FILE): return open(PASSWORD_FILE).read()
    try:
        pw = input("Password to store until next reboot: ")
    except KeyboardInterrupt:
        sys.exit(0)
    with open(PASSWORD_FILE, 'w') as f: f.write(pw)
    return pw

# Encrypt/Decrypt text
def encrypt(plaintext, passphrase):
    key, iv = sha256(passphrase.encode()).digest(), os.urandom(AES.block_size)
    return base64.b64encode(iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext.encode(), AES.block_size))).decode()

def decrypt(ciphertext, passphrase):
    try:
        decoded = base64.b64decode(ciphertext)
        return unpad(AES.new(sha256(passphrase.encode()).digest(), AES.MODE_CBC, decoded[:AES.block_size]).decrypt(decoded[AES.block_size:]), AES.block_size).decode()
    except (ValueError, KeyError): return None

# Image Encrypt/Decrypt
def derive_key(password):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=password.encode(), iterations=100000, backend=default_backend())
    return kdf.derive(password.encode())

def encrypt_image(image, key):
    iv = secrets.token_bytes(16)
    img_data = io.BytesIO(); image.save(img_data, format="PNG")
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
    encrypted_data = cipher.encryptor().update(img_data.getvalue()) + cipher.encryptor().finalize()
    return base64.b64encode(iv + encrypted_data)

def decrypt_image(encrypted_data, key):
    decoded = base64.b64decode(encrypted_data)
    iv, encrypted_img = decoded[:16], decoded[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
    decrypted_data = cipher.decryptor().update(encrypted_img) + cipher.decryptor().finalize()
    return Image.open(io.BytesIO(decrypted_data))
def display_image():
    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        try:
            from tkinter import Tk, Label
            from PIL import ImageTk
            root = Tk()
            root.title("Image")
            tk_image = ImageTk.PhotoImage(decrypted_image)
            label = Label(root, image=tk_image)
            label.pack()
            root.mainloop()
        except ImportError:
            print("To display the image, please install the pk package!")
# Main logic
if len(sys.argv) > 1:
    if sys.argv[1] == "-n":
        pw = input("Password to store until next reboot: ")
        copy_to_clipboard(pw)
        with open(PASSWORD_FILE, 'w') as f: f.write(pw)
        print(f"New password saved to {PASSWORD_FILE} and copied to clipboard.")
        sys.exit(0)
    elif sys.argv[1] == "-p":
        password = prefix_password+''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=30))
        copy_to_clipboard(password)
        with open(PASSWORD_FILE, 'w') as f: f.write(password)
        print(f"New random password saved to {PASSWORD_FILE} and copied to clipboard.")
        sys.exit(0)

clipboard_content = get_from_clipboard()
password = password_logic()

if prefix_text.encode() in clipboard_content:
    content = clipboard_content.decode()
    content = re.sub(r"@[^&]*&&|@.*$|<.*?>", "", content).replace(" ", "")
    text = decrypt(content, password) or "Incorrect password."
    print("Decrypted text:", text)
    copy_to_clipboard("")
elif clipboard_content.startswith(prefix_image.encode()):
    try:
        decrypted_image = decrypt_image(clipboard_content[len(prefix_image):], derive_key(password))
        img_bytes = io.BytesIO()
        decrypted_image.save(img_bytes, format="PNG")
        copy_to_clipboard(img_bytes.getvalue())
        print("Image decrypted from text and copied.")
        display_image()
    except (OSError, binascii.Error):
        print("Please click the download button on the text block")
        copy_to_clipboard("")
elif os.path.exists(message_file_path):
    with open(message_file_path, 'rb') as f:
        clipboard_content = f.read()
    if clipboard_content.startswith(prefix_image.encode()):
        try:
            decrypted_image = decrypt_image(clipboard_content[len(prefix_image):], derive_key(password))
            img_bytes = io.BytesIO()
            decrypted_image.save(img_bytes, format="PNG")
            copy_to_clipboard(img_bytes.getvalue())
            print("Image decrypted from file and copied.")
            display_image()
        except UnidentifiedImageError:
            os.remove(message_file_path)
            print("Incorrect password!")
            sys.exit(1)

    os.remove(message_file_path)
else:
    try:
        image = Image.open(io.BytesIO(clipboard_content))
        encrypted_image = encrypt_image(image, derive_key(password))
        copy_to_clipboard(prefix_image.encode() + encrypted_image)
        print("Image encrypted and copied.")
    except (UnidentifiedImageError, ValueError):
        try:
            text = encrypt(input("Text Input: "), password)
        except KeyboardInterrupt:
            sys.exit(0)
        copy_to_clipboard(prefix_text + text)
        print("Encrypted text copied to clipboard.")
