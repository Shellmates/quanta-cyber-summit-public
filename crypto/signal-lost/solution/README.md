# Signal Lost

## Write-up

This challenge combines **XOR key reuse** (two-time pad) with a **Morse-encoded known plaintext**. Both ciphertexts are encrypted with the same key; the known message is given in Morse so the player must decode it first, then apply the XOR math.

### Idea

- **c1** = flag XOR key (repeating)
- **c2** = known_plaintext XOR key (same key, repeating)
- **message_morse.txt** = known_plaintext encoded in Morse code

Because the key is the same: **c1 XOR c2 = flag XOR known_plaintext**. So **flag = (c1 XOR c2) XOR known_plaintext** (byte by byte, for the length of the flag).

### Steps

1. **Decode the Morse file**  
   Decode `message_morse.txt` to get the known plaintext. Standard Morse: letters A–Z, space between letters, `/` or double space between words.  
   Result: `IN CRYPTOGRAPHY REUSING A KEY CAN BE DANGEROUS`

2. **Load the ciphertexts**  
   Read `ciphertext1.hex` and `ciphertext2.hex` as hex and convert to bytes.

3. **Apply the XOR**  
   - xor_stream = c1 XOR c2 (for each byte index; truncate to the shorter length if needed).  
   - known_bytes = known_plaintext string encoded as UTF-8.  
   - flag_bytes = xor_stream XOR known_bytes (for the first len(flag) bytes, i.e. first 35 bytes).  
   So: `flag = bytes(a ^ b for a, b in zip(bytes.fromhex(c1_hex), bytes.fromhex(c2_hex)))[:35]` then XOR with the first 35 bytes of the known plaintext.  
   Or: `flag = bytes((a ^ b ^ c) for a, b, c in zip(c1, c2, known_plaintext_bytes))` and truncate to the length of the flag (35 bytes).

4. **Get the flag**  
   Decode the resulting bytes as UTF-8: `shellmates{m0rs3_4nd_x0r_k3y_r3us3}`

### Concepts

- **Key reuse**: If the same key is used for two messages, then c1 XOR c2 = m1 XOR m2. With one known message (m2), the other (m1) is recovered without ever recovering the key.
- **Morse**: Adds a decoding step so the challenge is not “just XOR”; the player must decode the known plaintext from Morse first.

## Flag

`shellmates{m0rs3_4nd_x0r_k3y_r3us3}`
