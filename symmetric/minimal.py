import subprocess, base64, os, platform, sys
from hashlib import sha256
try:
    from Cryptodome.Util.Padding import pad, unpad
    from Cryptodome.Cipher import AES
except ModuleNotFoundError:
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Cipher import AES
    
password = "PASSWORD_GOES_HERE"

def encrypt(plaintext, passphrase):
    key = sha256(passphrase.encode()).digest()
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = pad(plaintext.encode(), AES.block_size)
    ciphertext = iv + cipher.encrypt(padded_plaintext)
    return base64.b64encode(ciphertext).decode()
def decrypt(ciphertext, passphrase):
    key = sha256(passphrase.encode()).digest()
    ciphertext = base64.b64decode(ciphertext)
    iv = ciphertext[:AES.block_size]
    ciphertext = ciphertext[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()
input_text = input("Input text: ")
if input_text.startswith("&&"):
    decrypted_text = decrypt(input_text[2:], password)
    print("Decrypted text:", decrypted_text)
else:
    encrypted_text = encrypt(input_text, password)
    encrypted_text = ("&&" + encrypted_text)
    print("Encrypted text:")
    print(encrypted_text)
