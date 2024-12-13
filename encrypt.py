import sys, subprocess, secrets, io, os, base64, random, string, re
from PIL import Image, UnidentifiedImageError
from hashlib import sha256
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ModuleNotFoundError:
    print("please install python-pyrcyptodome")

# Constants
PASSWORD_FILE = "/tmp/key"
prefix_text, prefix_password, prefix_image = "$$", "@@", "££"

# Clipboard stuff
def copy_to_clipboard(data):  # Copies to clipboard for Wayland or X11
    cmd = ["wl-copy"] if os.environ.get("XDG_SESSION_TYPE") == "wayland" else ["xclip", "-selection", "clipboard"]
    subprocess.run(cmd, input=data if isinstance(data, bytes) else data.encode())

def get_from_clipboard():  # Reads clipboard content (text or binary)
    cmd = ["wl-paste", "--no-newline"] if os.environ.get("XDG_SESSION_TYPE") == "wayland" else ["xclip", "-o", "-selection", "clipboard"]
    data = subprocess.run(cmd, stdout=subprocess.PIPE).stdout
    return data  # Return raw binary data (no decode)

# Password management
def password_logic():
    if clipboard_content.startswith(prefix_password.encode()):  # Save clipboard content as password
        with open(PASSWORD_FILE, 'w') as f:
            f.write(clipboard_content.decode())
        print(f"New password saved to {PASSWORD_FILE}.")
        sys.exit(0)
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            return f.read()
    pw = input("Password to store until next reboot: ")
    with open(PASSWORD_FILE, 'w') as f:
        f.write(pw)
    return pw

# Text encryption and decryption
def encrypt(plaintext, passphrase):
    key, iv = sha256(passphrase.encode()).digest(), os.urandom(AES.block_size)
    return base64.b64encode(iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext.encode(), AES.block_size))).decode()

def decrypt(ciphertext, passphrase):
    try:
        key, decoded = sha256(passphrase.encode()).digest(), base64.b64decode(ciphertext)
        return unpad(AES.new(key, AES.MODE_CBC, decoded[:AES.block_size]).decrypt(decoded[AES.block_size:]), AES.block_size).decode()
    except (ValueError, KeyError):
        return None

# Image encryption and decryption
def derive_key(password):
    salt = password.encode()
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    return kdf.derive(password.encode())

def encrypt_image(image: Image.Image, key: bytes):
    iv = secrets.token_bytes(16)
    img_data = io.BytesIO(); image.save(img_data, format="PNG")
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
    encrypted_data = cipher.encryptor().update(img_data.getvalue()) + cipher.encryptor().finalize()
    return base64.b64encode(iv + encrypted_data)

def decrypt_image(encrypted_data: bytes, key: bytes):
    decoded = base64.b64decode(encrypted_data)
    iv, encrypted_img = decoded[:16], decoded[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
    decrypted_data = cipher.decryptor().update(encrypted_img) + cipher.decryptor().finalize()
    return Image.open(io.BytesIO(decrypted_data))
# Main logic
# Handle flags
if len(sys.argv) > 1:
    if sys.argv[1] == "-n":
        # Prompt for a new password
        pw = input("password to store until next reboot: ")
        copy_to_clipboard(pw)
        with open(PASSWORD_FILE, 'w') as f:
            f.write(pw)
        print(f"New password saved to {PASSWORD_FILE} and copied to clipboard.")
        sys.exit(0)
    elif sys.argv[1] == "-p":
        # Generate a random password
        password = "@@"+''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=30))
        copy_to_clipboard(password)
        with open(PASSWORD_FILE, 'w') as f:
            f.write(password)
        print(f"New random password saved to {PASSWORD_FILE} and copied to clipboard.")
        sys.exit(0)
clipboard_content = get_from_clipboard()
password = password_logic()

# Handle figuring out what is to be copied or pasted
try:
    if clipboard_content.startswith(prefix_text.encode()):  # Handle text encryption/decryption
        text = decrypt(clipboard_content[2:].decode(), password) or "Incorrect password."
        print("Decrypted text:", text)
        copy_to_clipboard("")  # Clear clipboard
    elif clipboard_content.startswith(prefix_password.encode()):  # Save new password
        with open(PASSWORD_FILE, 'w') as f:
            f.write(clipboard_content[2:].decode())
        print(f"New password saved to {PASSWORD_FILE}.")
        sys.exit(0)
    elif clipboard_content.startswith(prefix_image.encode()):  # Handle image decryption
        try:
            decrypted_image = decrypt_image(clipboard_content[len(prefix_image):], derive_key(password))
            img_bytes = io.BytesIO()
            decrypted_image.save(img_bytes, format="PNG")
            copy_to_clipboard(img_bytes.getvalue())
            print("Image decrypted and copied.")
        except Exception as e:
            print(f"Error decrypting image: {e}")
    else:  # If the content is not text or image, attempt to encrypt it
        try:
            image = Image.open(io.BytesIO(clipboard_content))  # Attempt to open as image
            encrypted_image = encrypt_image(image, derive_key(password))
            copy_to_clipboard(prefix_image.encode() + encrypted_image)
            print("Image encrypted and copied.")
        except UnidentifiedImageError:  # Handle text encryption if not an image
            text = encrypt(input("Text Input: "), password)
            copy_to_clipboard(prefix_text + text)
            print("Encrypted text copied to clipboard.")
except Exception:
    print("what are you feeding me im frightned")
