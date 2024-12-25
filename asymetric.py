import os, subprocess
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def get_clipboard_tool():
    return ["wl-copy"] if os.environ.get("XDG_SESSION_TYPE") == "wayland" else ["xclip", "-selection", "clipboard"]
def clipboard_content():
    try:
        return subprocess.run(get_clipboard_tool() + ["-o"], capture_output=True, text=True, check=True).stdout.strip()
    except:
        print("what slop is on your clipboard lmao")
def write_to_clipboard(data):
    subprocess.run(get_clipboard_tool(), input=data.encode(), check=True)
def generate_keypair():
    key = RSA.generate(2048)
    name = input("Enter name for key pair: ").strip()
    with open(f"{name}_private.key", "wb") as priv_file, open(f"{name}_public.key", "wb") as pub_file:
        priv_file.write(key.export_key())
        pub_file.write(key.publickey().export_key())
    print(f"New keypair: {name}_private.key and {name}_public.key")
def encrypt_message():
    public_keys = [f.replace('_public.key', '') for f in os.listdir() if f.endswith("_public.key")]
    if not public_keys:
        print("Make some friends and come back (no public keys).")
    pub_keys_input = []
    while (pub_key_name := input(f"Choose recipient(s) {public_keys} (q to finish): ").strip()) != 'q':
        if pub_key_name in public_keys:
            pub_keys_input.append(pub_key_name)
        else:
            print(f"I don't know any {pub_key_name}")
    message = input("Message to encrypt: ")
    try:
        encrypted_msgs = [
            PKCS1_OAEP.new(RSA.import_key(open(f"{key}_public.key", "rb").read())).encrypt(message.encode()).hex()
            for key in pub_keys_input
        ]
        print(f"Private key option(s): {private_keys}")
        signature = pkcs1_15.new(RSA.import_key(open(f"{input('Private key to sign with: ').strip()}_private.key", 'rb').read())).sign(SHA256.new(message.encode()))
        encrypted_data = "$$".join(encrypted_msgs) + f"||{signature.hex()}"
        write_to_clipboard(encrypted_data)
        print("Encrypted message copied.")
    except (UnboundLocalError, FileNotFoundError):
        print("who tf is that")
def decrypt_message():
    encrypted_data = clipboard_content()
    if not encrypted_data:
        print("Clipboard is empty.")
    if not private_keys:
        print("No private keys in directory. make a keypair first")
    priv_key_name = input(f"Choose private key {private_keys}: ").strip()
    if priv_key_name not in private_keys:
        print(f"who tf is {priv_key_name}")
    private_key = RSA.import_key(open(f"{priv_key_name}_private.key", "rb").read())
    encrypted_msgs, signature = encrypted_data.split("||")[:-1], bytes.fromhex(encrypted_data.split("||")[-1])
    decrypted_message = None
    for encrypted_msg in encrypted_msgs[0].split("$$"):
        try:
            decrypted_message = PKCS1_OAEP.new(private_key).decrypt(bytes.fromhex(encrypted_msg)).decode()
            break
        except ValueError:
            continue
    if not decrypted_message:
        print("whaever is on ur clioboard is WRONG")
    sender_pub_key_name = input("What public key to use (Who sent it?): ").strip()
    sender_public_key = RSA.import_key(open(f"{sender_pub_key_name}_public.key", "rb").read())
    try:
        pkcs1_15.new(sender_public_key).verify(SHA256.new(decrypted_message.encode()), signature)
        print(f"Decrypted message: {decrypted_message}")
    except (ValueError, TypeError):
        print("public key used does not match message sender")
private_keys = [f.replace('_private.key', '') for f in os.listdir() if f.endswith("_private.key")]
actions = {"1": generate_keypair, "2": encrypt_message, "3": decrypt_message}
print("1. Generate Key Pair\n2. Encrypt Message\n3. Decrypt Message")
actions.get(input("Choose action: "), lambda: print("Invalid choice."))()
