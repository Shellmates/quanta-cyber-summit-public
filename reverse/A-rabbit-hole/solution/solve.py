key = [0x62, 0x75, 0x67, 0x73, 0x62, 0x75, 0x6e, 0x6e, 0x79]
key_len = len(key)

encrypted_hex = "191305101d1408353a011b24231d2e3b77193b39078586867301698a926c6a595f470f18695f83111814"
encrypted = [int(encrypted_hex[i:i+2], 16) for i in range(0, len(encrypted_hex), 2)]

def inverse_gray(n):
    inv = 0
    while n:
        inv ^= n
        n >>= 1
    return inv

def decode_gray(gray_list):
    return [inverse_gray(n) for n in gray_list]

def decrypt3(data):
    return [data[i] ^ i for i in range(len(data))]

def decrypt2(data, data_len):
    decrypted = []
    
    for i in range(data_len):
        encrypted_value = data[i]
        
        even_byte = (encrypted_value - i) % 256
        odd_byte = (encrypted_value + i) % 256
        
        if even_byte % 2 == 0:
            decrypted.append(even_byte)
        else:
            decrypted.append(odd_byte)
    
    return decrypted

def decrypt1(data, key, key_len):
    return [data[i] ^ key[i % key_len] for i in range(len(data))]

data = decode_gray(encrypted)
data = decrypt3(data)
data = decrypt2(data, len(data))
data = decrypt1(data, key, key_len)

flag = ''.join(chr(c) for c in data)
print(f"Flag => {flag}" )
