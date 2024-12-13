import sys, subprocess, secrets, io, os, base64, random, string, re
from PIL import Image, UnidentifiedImageError
from hashlib import sha256
try:
    # Try importing the required cryptographic libraries.
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ModuleNotFoundError:  # If a required module is not installed
    # Inform the user that pycryptodome needs to be installed and exit with an error code.
    print("Please install python-pycryptodome")
    sys.exit(1)  # Exit the program with a failure code

# Define a file path to store the password temporarily in RAM.
PASSWORD_FILE = "/tmp/key"  # This ensures the password is not persisted across reboots.

# Define prefixes to distinguish between text, password, and image data.
prefix_text, prefix_password, prefix_image = "$$", "@@", "££"  # These help the program decide how to process clipboard data.

# Utilities

def copy_to_clipboard(data):  # Function to copy data to the clipboard
    # Check the session type (Wayland or X11) and choose the appropriate clipboard tool.
    cmd = ["wl-copy"] if os.environ.get("XDG_SESSION_TYPE") == "wayland" else ["xclip", "-selection", "clipboard"]
    # Run the clipboard command, encoding the data if it's not already bytes.
    subprocess.run(cmd, input=data if isinstance(data, bytes) else data.encode())

def get_from_clipboard():  # Function to get data from the clipboard
    # Check the session type and choose the appropriate tool for retrieving clipboard content.
    cmd = ["wl-paste", "--no-newline"] if os.environ.get("XDG_SESSION_TYPE") == "wayland" else ["xclip", "-o", "-selection", "clipboard"]
    # Start a subprocess to capture the clipboard content (may include binary data).
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Communicate with the subprocess to retrieve the data from the clipboard.
    data, _ = process.communicate()
    return data  # Return the captured data

# Password management
def password_logic():  # Function to manage password storage and retrieval
    # Check if the clipboard content starts with the password prefix.
    if clipboard_content.startswith(prefix_password.encode()):
        # Save the clipboard content as the new password in the password file.
        with open(PASSWORD_FILE, 'w') as f:
            f.write(clipboard_content.decode())  # Write the password to the file.
        print(f"New password saved to {PASSWORD_FILE}.")
        sys.exit(0)  # Exit after saving the password.
    # If the password file exists, retrieve and return the stored password.
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            return f.read()  # Read and return the password.
    # If no password exists, prompt the user to enter a password.
    pw = input("Password to store until next reboot: ")
    with open(PASSWORD_FILE, 'w') as f:
        f.write(pw)  # Save the entered password to the file.
    return pw  # Return the newly entered password

# Text encryption and decryption
def encrypt(plaintext, passphrase):
    # Generate an encryption key using SHA256 and a random initialization vector (IV).
    key, iv = sha256(passphrase.encode()).digest(), os.urandom(AES.block_size)
    # Encrypt the plaintext, pad it to the block size, and encode it in base64.
    return base64.b64encode(iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext.encode(), AES.block_size))).decode()

def decrypt(ciphertext, passphrase):
    try:
        # Generate the encryption key and decode the base64-encoded ciphertext.
        key, decoded = sha256(passphrase.encode()).digest(), base64.b64decode(ciphertext)
        # Decrypt the ciphertext and remove padding to retrieve the plaintext.
        return unpad(AES.new(key, AES.MODE_CBC, decoded[:AES.block_size]).decrypt(decoded[AES.block_size:]), AES.block_size).decode()
    except (ValueError, KeyError):
        # Return None if decryption fails due to incorrect password or corrupted data.
        return None

# Image encryption and decryption
def derive_key(password):
    # Use PBKDF2HMAC to derive a 256-bit key from the password.
    salt = password.encode()  # Use the password itself as the salt.
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Generate a 256-bit key.
        salt=salt,
        iterations=100000,  # Perform 100,000 iterations for security.
        backend=default_backend(),
    )
    return kdf.derive(password.encode())  # Derive and return the key

def encrypt_image(image: Image.Image, key: bytes):
    # Generate a random initialization vector (IV).
    iv = secrets.token_bytes(16)
    # Save the image to an in-memory binary stream in PNG format.
    img_data = io.BytesIO(); image.save(img_data, format="PNG")
    # Create a cipher object using AES with CFB8 mode and the derived key.
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
    # Encrypt the image data and finalize the encryption.
    encrypted_data = cipher.encryptor().update(img_data.getvalue()) + cipher.encryptor().finalize()
    # Return the encrypted data encoded in base64.
    return base64.b64encode(iv + encrypted_data)

def decrypt_image(encrypted_data: bytes, key: bytes):
    # Decode the base64-encoded encrypted data.
    decoded = base64.b64decode(encrypted_data)
    # Extract the IV and the encrypted image data.
    iv, encrypted_img = decoded[:16], decoded[16:]
    # Create a cipher object using AES with CFB8 mode and the derived key.
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
    # Decrypt the image data and return it as an Image object.
    decrypted_data = cipher.decryptor().update(encrypted_img) + cipher.decryptor().finalize()
    return Image.open(io.BytesIO(decrypted_data))

# Process command-line arguments
if len(sys.argv) > 1:
    if sys.argv[1] == "-n":
        # If the user passed the -n flag, prompt for a new password.
        pw = input("password to store until next reboot: ")
        with open(PASSWORD_FILE, 'w') as f:
            f.write(pw)  # Save the new password.
        print(f"New password saved to {PASSWORD_FILE}")
        sys.exit(0)  # Exit after saving the password.
    elif sys.argv[1] == "-p":
        # If the user passed the -p flag, generate a new random password.
        password = "@@" + ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=30))
        copy_to_clipboard(password)  # Copy the password to the clipboard.
        with open(PASSWORD_FILE, 'w') as f:
            f.write(password)  # Save the new password.
        print(f"New random password saved to {PASSWORD_FILE} and copied to clipboard.")
        sys.exit(0)  # Exit after saving the password.

# Main logic starts here.
clipboard_content = get_from_clipboard()  # Retrieve the current clipboard content.
password = password_logic()  # Retrieve or prompt for the password.

try:
    if clipboard_content.startswith(prefix_text.encode()):  # If clipboard content starts with text prefix
        # Decrypt the text using the password and print it, or indicate if the password is incorrect.
        text = decrypt(clipboard_content[2:].decode(), password) or "Incorrect password."
        print("Decrypted text:", text)
        copy_to_clipboard("")  # Clear the clipboard.
    elif clipboard_content.startswith(prefix_password.encode()):  # If clipboard content starts with password prefix
        password_logic()  # Save the clipboard content as the new password.
    elif clipboard_content.startswith(prefix_image.encode()):  # If clipboard content starts with image prefix
        # Decrypt the image and copy it back to the clipboard.
        decrypted_image = decrypt_image(clipboard_content[len(prefix_image):], derive_key(password))
        img_bytes = io.BytesIO(); decrypted_image.save(img_bytes, format="PNG")
        copy_to_clipboard(img_bytes.getvalue())
        print("Image decrypted and copied")
    else:  # If no prefixes match, attempt to encrypt clipboard content as an image or text.
        try:
            # Try opening the clipboard content as an image.
            image = Image.open(io.BytesIO(clipboard_content))
            encrypted_image = encrypt_image(image, derive_key(password))
            copy_to_clipboard(prefix_image.encode() + encrypted_image)  # Copy the encrypted image to the clipboard.
            print("Image encrypted and copied")
        except (UnidentifiedImageError, ValueError):
            # If it's not an image, prompt the user for text input and encrypt it.
            text = encrypt(input("Text Input: "), password)
            copy_to_clipboard(prefix_text + text)  # Copy the encrypted text to the clipboard.
            print("Encrypted text copied to clipboard.")
except Exception:
    # If any unexpected error occurs, say a funny message.
    print("what are you trying to feed me im frightened")
