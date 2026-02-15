#!/usr/bin/env python3
"""
Generator for the LCG Orbit (hard crypto) challenge.

We use a 64-bit Linear Congruential Generator (LCG):
    x_{n+1} = (A * x_n + C) mod 2^64

We build a keystream from successive 64-bit states and XOR it with:
  - a known plaintext (provided to players)
  - a secret flag  (to be recovered)

Players see:
  - plaintext_known.txt  (the known plaintext in clear)
  - ciphertext_known.hex (hex-encoded XOR of known plaintext with keystream)
  - ciphertext_flag.hex  (hex-encoded XOR of flag with *later* keystream blocks)
  - encrypt.py           (LCG structure, but A, C, seed removed)
"""

import os
import random

FLAG = b"shellmates{lCG_prng_k3Y_r3C0v3ry}"
PLAINTEXT_KNOWN = (
    b"THIS IS A KNOWN PLAINTEXT USED TO ANALYZE A 64-BIT LCG STREAM.\n"
    b"ONCE YOU RECOVER THE GENERATOR, YOU CAN DECRYPT THE SECRET FLAG.\n"
)

MOD = 2**64


def lcg_next(x: int, a: int, c: int) -> int:
    return (a * x + c) % MOD


def keystream(a: int, c: int, seed: int, n_blocks: int):
    """Yield n_blocks successive 8-byte blocks from the LCG."""
    x = seed
    for _ in range(n_blocks):
        x = lcg_next(x, a, c)
        yield x.to_bytes(8, "big")


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings (b is repeated if shorter)."""
    return bytes(x ^ b[i % len(b)] for i, x in enumerate(a))


def main() -> None:
    random.seed(1337)
    # Secret LCG parameters (not revealed to players)
    A = 0x5851F42D4C957F2D  # odd multiplier
    C = 0x14057B7EF767814F  # increment
    SEED = random.getrandbits(64)

    base_dir = os.path.dirname(__file__)

    # Build keystream for known plaintext
    blocks_known = (len(PLAINTEXT_KNOWN) + 7) // 8
    ks_blocks = list(keystream(A, C, SEED, blocks_known))
    ks_known = b"".join(ks_blocks)[: len(PLAINTEXT_KNOWN)]

    ciphertext_known = xor_bytes(PLAINTEXT_KNOWN, ks_known)

    # Continue keystream for flag (from where we stopped)
    # Last state used in ks_blocks is the last element's state; recompute it:
    # We can get the last x from ks_blocks[-1]
    last_x = int.from_bytes(ks_blocks[-1], "big")
    blocks_flag = (len(FLAG) + 7) // 8
    ks_blocks_flag = []
    x = last_x
    for _ in range(blocks_flag):
        x = lcg_next(x, A, C)
        ks_blocks_flag.append(x.to_bytes(8, "big"))
    ks_flag = b"".join(ks_blocks_flag)[: len(FLAG)]

    ciphertext_flag = xor_bytes(FLAG, ks_flag)

    # Write files for the challenge
    with open(os.path.join(base_dir, "plaintext_known.txt"), "wb") as f:
        f.write(PLAINTEXT_KNOWN)

    with open(os.path.join(base_dir, "ciphertext_known.hex"), "w") as f:
        f.write(ciphertext_known.hex())

    with open(os.path.join(base_dir, "ciphertext_flag.hex"), "w") as f:
        f.write(ciphertext_flag.hex())

    # Encrypt script shown to players (parameters removed)
    encrypt_py = """#!/usr/bin/env python3
MOD = 2**64

# NOTE: Parameters A, C and SEED were secret and removed from this file.
#       They were randomly chosen 64-bit integers with A odd.
#       The generator is:
#           x_{n+1} = (A * x_n + C) mod 2**64
#
# This script shows how the keystream was *conceptually* generated and used,
# but not the actual values of A, C, SEED.


def lcg_next(x: int, a: int, c: int) -> int:
    return (a * x + c) % MOD


def keystream(a: int, c: int, seed: int, n_blocks: int):
    x = seed
    for _ in range(n_blocks):
        x = lcg_next(x, a, c)
        yield x.to_bytes(8, "big")


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ b[i % len(b)] for i, x in enumerate(a))


if __name__ == "__main__":
    print("This file documents the LCG structure used in the challenge.")
"""

    with open(os.path.join(base_dir, "encrypt.py"), "w") as f:
        f.write(encrypt_py)

    print("Generated plaintext_known.txt, ciphertext_known.hex, ciphertext_flag.hex, encrypt.py")


if __name__ == "__main__":
    main()

