from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

with open("encrypted.bin", "rb") as f:
    data = f.read()

iv = data[:16]
ciphertext = data[16:]
key = b"1337133713371337"

cipher = AES.new(key, AES.MODE_CBC, iv)
try:
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    print(f"flag : {decrypted.decode()}")
except ValueError as e:
    print(f"Decryption failed: {e}")
