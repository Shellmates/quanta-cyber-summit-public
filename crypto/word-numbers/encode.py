#!/usr/bin/env python3
"""
Encoder for the Word Numbers challenge.
Converts a message (A-Z) to English number words (1-26).
Usage: python encode.py  -> encodes the default flag
       python encode.py "MESSAGE" -> encodes the given message
"""

# English words for numbers 1 to 26 (A=1 ... Z=26)
NUM_TO_ENGLISH = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
    21: "twenty-one",
    22: "twenty-two",
    23: "twenty-three",
    24: "twenty-four",
    25: "twenty-five",
    26: "twenty-six",
}

ENGLISH_TO_NUM = {v: k for k, v in NUM_TO_ENGLISH.items()}


def encode(plaintext: str) -> str:
    """Encode a message (letters A-Z only) to English words."""
    result = []
    for c in plaintext.upper():
        if "A" <= c <= "Z":
            result.append(NUM_TO_ENGLISH[ord(c) - ord("A") + 1])
    return " ".join(result)


def decode(ciphertext: str) -> str:
    """Decode a sequence of English words to a message (A-Z)."""
    words = ciphertext.lower().split()
    result = []
    i = 0
    while i < len(words):
        # Try single word first, then two, then three (avoids merging "twenty"+"five" into "twenty-five")
        for length in (1, 2, 3):
            if i + length <= len(words):
                candidate = "-".join(words[i : i + length])
                if candidate in ENGLISH_TO_NUM:
                    result.append(chr(ENGLISH_TO_NUM[candidate] - 1 + ord("A")))
                    i += length
                    break
        else:
            i += 1
    return "".join(result)


if __name__ == "__main__":
    import sys
    FLAG = "shellmates{wordnumbersarefun}"
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        msg = FLAG
    # Only encode letters (flag format to be inferred by the player)
    letters_only = "".join(c for c in msg.upper() if "A" <= c <= "Z")
    print(encode(letters_only))
