import sys, subprocess, secrets, io, os, base64
from PIL import Image, UnidentifiedImageError
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

PASSWORD_FILE = "/tmp/key"

def get_password():
    with open(PASSWORD_FILE, "rb") as f:
        return f.read().strip()

def derive_key(password):
    salt = get_password()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    return kdf.derive(password)

def encrypt_image(image: Image.Image, key: bytes):
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_data = img_bytes.getvalue()
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(img_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data)

def decrypt_image(encrypted_data: bytes, key: bytes):
    encrypted_data = base64.b64decode(encrypted_data)
    iv, encrypted_img = encrypted_data[:16], encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_img) + decryptor.finalize()
    return Image.open(io.BytesIO(decrypted_data))

def copy_to_clipboard(data: bytes):
    process = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
    process.communicate(input=data)

def get_from_clipboard():
    process = subprocess.Popen(["wl-paste"], stdout=subprocess.PIPE)
    clipboard_data, _ = process.communicate()
    return clipboard_data

password = get_password()
key = derive_key(password)
clipboard_data = get_from_clipboard()
try:
    try:
        image = Image.open(io.BytesIO(clipboard_data))
        encrypted_image = encrypt_image(image, key)
        copy_to_clipboard(encrypted_image)
        print("Image encrypted and copied")
    except UnidentifiedImageError:
        decrypted_image = decrypt_image(clipboard_data, key)
        img_bytes = io.BytesIO()
        decrypted_image.save(img_bytes, format="PNG")
        copy_to_clipboard(img_bytes.getvalue())
        print("Image decrypted and copied")
except Exception:
    print("No image on clipboard")
