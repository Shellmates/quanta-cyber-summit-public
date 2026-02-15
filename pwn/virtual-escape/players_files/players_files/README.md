# ByteForge VM

Custom virtual machine challenge.

## Files

- `vm` - The target binary
- `asm.py` - Assembler tool

## Usage

```bash
# Write assembly
cat > test.asm << 'EOF'
PUSH 42
PRINT
HALT
EOF

# Assemble to bytecode
./asm.py test.asm test.bin

# Run
./vm test.bin
```

## Goal

Exploit the VM to get the flag.

## Remote Exploitation

Once you successfully exploit the VM locally, test your exploit against the remote service:

```bash
nc <server> <port> < exploit.bin
```

Good luck! 🚀
