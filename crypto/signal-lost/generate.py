#!/usr/bin/env python3
"""
Generator for the Signal Lost challenge.
Produces: ciphertext1.hex, ciphertext2.hex, message_morse.txt
- c1 = flag XOR key (repeating)
- c2 = known_plaintext XOR key (same key, repeating)
- message_morse.txt = known_plaintext encoded in Morse
So: c1 XOR c2 = flag XOR known_plaintext => flag = (c1 XOR c2) XOR known_plaintext
"""

import os
import random

FLAG = b"shellmates{m0rs3_4nd_x0r_k3y_r3us3}"
KNOWN_PLAINTEXT = b"IN CRYPTOGRAPHY REUSING A KEY CAN BE DANGEROUS"

# Morse code (A-Z, 0-9, space)
MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    " ": " ",
}


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings (b is repeated if shorter)."""
    return bytes(x ^ b[i % len(b)] for i, x in enumerate(a))


def text_to_morse(text: str) -> str:
    """Encode ASCII text to Morse (letters, digits, space)."""
    out = []
    for c in text.upper():
        if c in MORSE:
            out.append(MORSE[c])
    return " ".join(out).replace("  ", " / ").strip()


def main():
    random.seed(42)
    key_len = max(len(FLAG), len(KNOWN_PLAINTEXT))
    key = bytes(random.randint(0, 255) for _ in range(key_len))

    c1 = xor_bytes(FLAG, key)
    c2 = xor_bytes(KNOWN_PLAINTEXT, key)

    base = os.path.dirname(__file__)
    with open(os.path.join(base, "ciphertext1.hex"), "w") as f:
        f.write(c1.hex())
    with open(os.path.join(base, "ciphertext2.hex"), "w") as f:
        f.write(c2.hex())

    morse_msg = text_to_morse(KNOWN_PLAINTEXT.decode("utf-8"))
    with open(os.path.join(base, "message_morse.txt"), "w") as f:
        f.write(morse_msg)

    print("Generated: ciphertext1.hex, ciphertext2.hex, message_morse.txt")


if __name__ == "__main__":
    main()
