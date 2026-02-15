#!/usr/bin/env python3
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
