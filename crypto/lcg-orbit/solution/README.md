# LCG Orbit

## Write-up

This challenge uses a **64-bit Linear Congruential Generator (LCG)** as a keystream generator for a XOR-based stream cipher.  
Two messages are encrypted with the **same LCG**; one of them is fully known in clear. The LCG parameters and seed are removed.

We have:

- `plaintext_known.txt`          – known plaintext \(P\)  
- `ciphertext_known.hex`        – \(C_k = P \oplus K_k\)  
- `ciphertext_flag.hex`         – \(C_f = F \oplus K_f\) (flag \(F\), unknown)  
- `encrypt.py`                  – describes the LCG structure  

The LCG:

\[
x_{n+1} = (A x_n + C) \bmod 2^{64}
\]

The keystream is built by taking successive 64-bit states and XORing them with the plaintext (block by block, big-endian).

### Step 1 – Recover the keystream blocks from the known plaintext

1. Read `plaintext_known.txt` as bytes \(P\).  
2. Read `ciphertext_known.hex` as bytes \(C_k\).  
3. Compute the keystream bytes for the known part:

\[
K_k = P \oplus C_k
\]

4. Group `K_k` into 8‑byte blocks and interpret each as a 64‑bit big‑endian integer:

```python
blocks = [int.from_bytes(K_k[i:i+8], "big") for i in range(0, len(K_k), 8)]
```

These integers are consecutive LCG states:  
\(x_1, x_2, x_3, \dots\) (up to the number of blocks in the known plaintext).

### Step 2 – Recover LCG parameters \(A\) and \(C\)

For any three consecutive states \(x_i, x_{i+1}, x_{i+2}\):

\[
\begin{aligned}
x_{i+1} &\equiv A x_i + C \pmod{2^{64}} \\
x_{i+2} &\equiv A x_{i+1} + C \pmod{2^{64}}
\end{aligned}
\]

Subtract:

\[
(x_{i+2} - x_{i+1}) \equiv A (x_{i+1} - x_i) \pmod{2^{64}}
\]

Let:
- \(d_1 = (x_{i+1} - x_i) \bmod 2^{64}\)  
- \(d_2 = (x_{i+2} - x_{i+1}) \bmod 2^{64}\)

Then:

\[
A \equiv d_2 \cdot d_1^{-1} \pmod{2^{64}}
\]

We need \(d_1\) to be invertible modulo \(2^{64}\), i.e. \(\gcd(d_1, 2^{64}) = 1\).  
Try multiple triples until you find one with \(d_1\) odd (coprime to \(2\)).

In Python, implement an extended GCD to get the modular inverse of \(d_1\) modulo \(2^{64}\), then compute \(A\).

Once \(A\) is known, recover \(C\) from:

\[
C \equiv x_{i+1} - A x_i \pmod{2^{64}}
\]

You can verify \(A, C\) by checking the recurrence on several consecutive blocks.

### Step 3 – Extend the keystream to the flag region

From the generation script logic (or from the challenge description), the keystream for the flag starts **after** the known plaintext blocks.  
Let:

- `blocks` be the list \([x_1, x_2, \dots, x_m]\) from the known plaintext.  
- `last_state = blocks[-1]`.

Generate further states using the recovered \(A, C\):

```python
MOD = 2**64
def lcg_next(x): return (A * x + C) % MOD

states_flag = []
x = last_state
for _ in range(n_flag_blocks):
    x = lcg_next(x)
    states_flag.append(x)
```

Convert these states to 8‑byte big‑endian blocks and concatenate to get `K_f`, the keystream bytes for the flag (truncate to the length of the flag ciphertext).

### Step 4 – Decrypt the flag

1. Read `ciphertext_flag.hex` as bytes \(C_f\).  
2. Compute:

\[
F = C_f \oplus K_f
\]

3. Decode `F` as ASCII/UTF‑8 to obtain the flag:

```text
shellmates{lCG_prng_k3Y_r3C0v3ry}
```

### Concepts

- **LCG weakness**: a linear congruential generator is fully determined by a small number of outputs; parameters and future states are recoverable, so it is **not** cryptographically secure.  
- **Stream cipher misuse**: using an LCG as a keystream generator, even with 64‑bit state, leaks enough structure to recover the key stream and decrypt messages.

## Flag

`shellmates{lCG_prng_k3Y_r3C0v3ry}`

