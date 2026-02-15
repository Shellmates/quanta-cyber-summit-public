from Crypto.Util.number import *
import random
from secret import FLAG as pt
import time


n = getPrime(2**10) * getPrime(2**10)
e = 0x10001

random.seed(int(time.time()/600))

while bytes_to_long(pt + b'n') < n:
    pt += random.randbytes(1)

pt = bytes_to_long(pt)
ct = pow(pt,e,n)

print(f'{n=}')
print(f'{ct=}')

resp = input('You wanna try? (y/n) ')
random.seed(int(time.time()))

if resp != "y":
    exit(0)

n ^= 1 << random.randint(0,n.bit_length())

ct = pow(pt,e,n)

print(f'{ct=}')
