#!/usr/bin/env python3
"""
ByteForge VM Assembler
Converts assembly-like syntax to VM bytecode
"""

import sys
import struct

# Opcode definitions
OPCODES = {
    'PUSH': 0x01,
    'POP': 0x02,
    'DUP': 0x03,
    
    'ADD': 0x10,
    'SUB': 0x11,
    'MUL': 0x12,
    
    'LOAD': 0x20,
    'STORE': 0x21,
    
    'JMP': 0x30,
    'JZ': 0x31,
    'CALL': 0x32,
    'RET': 0x33,
    
    'PRINT': 0x40,
    'GETINT': 0x41,
    
    'DUMP_REGS': 0xE0,
    'DUMP_STACK': 0xE1,
    'TRIGGER_ERROR': 0xF0,
    'HALT': 0xFF,
}

def parse_value(s):
    """Parse a numeric value (supports decimal and hex)"""
    s = s.strip()
    if s.startswith('0x') or s.startswith('0X'):
        return int(s, 16)
    return int(s)

def assemble(code):
    """Assemble code into bytecode"""
    bytecode = bytearray()
    labels = {}
    instructions = []
    
    # First pass: collect labels and instructions
    for line_num, line in enumerate(code.split('\n'), 1):
        # Remove comments
        if ';' in line:
            line = line[:line.index(';')]
        
        line = line.strip()
        if not line:
            continue
        
        # Check for label
        if ':' in line:
            label, rest = line.split(':', 1)
            labels[label.strip()] = len(bytecode)
            line = rest.strip()
            if not line:
                continue
        
        # Parse instruction
        parts = line.split()
        if not parts:
            continue
        
        op = parts[0].upper()
        if op not in OPCODES:
            print(f"Error on line {line_num}: Unknown opcode '{op}'")
            sys.exit(1)
        
        instructions.append((len(bytecode), op, parts[1:] if len(parts) > 1 else []))
        
        # Calculate bytecode size for this instruction
        bytecode.append(OPCODES[op])
        
        if op == 'PUSH':
            bytecode.extend([0] * 8)  # Placeholder for 64-bit value
        elif op in ['LOAD', 'STORE', 'JMP', 'JZ', 'CALL']:
            bytecode.extend([0] * 2)  # Placeholder for 16-bit value
    
    # Second pass: encode instructions with resolved labels
    bytecode = bytearray()
    
    for offset, op, args in instructions:
        bytecode.append(OPCODES[op])
        
        if op == 'PUSH':
            if not args:
                print(f"Error: PUSH requires an argument")
                sys.exit(1)
            val = parse_value(args[0])
            bytecode.extend(struct.pack('<Q', val))
        
        elif op in ['LOAD', 'STORE']:
            if not args:
                print(f"Error: {op} requires an argument")
                sys.exit(1)
            val = parse_value(args[0])
            bytecode.extend(struct.pack('<H', val))
        
        elif op in ['JMP', 'JZ', 'CALL']:
            if not args:
                print(f"Error: {op} requires an argument")
                sys.exit(1)
            
            # Check if it's a label or a number
            if args[0] in labels:
                addr = labels[args[0]]
            else:
                addr = parse_value(args[0])
            
            bytecode.extend(struct.pack('<H', addr))
    
    return bytes(bytecode)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.asm> <output.bin>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Read assembly code
    try:
        with open(input_file, 'r') as f:
            code = f.read()
    except IOError as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Assemble
    try:
        bytecode = assemble(code)
    except Exception as e:
        print(f"Assembly error: {e}")
        sys.exit(1)
    
    # Write bytecode
    try:
        with open(output_file, 'wb') as f:
            f.write(bytecode)
        print(f"Assembled {len(bytecode)} bytes to {output_file}")
    except IOError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
