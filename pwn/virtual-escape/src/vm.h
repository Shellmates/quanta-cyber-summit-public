#ifndef VM_H
#define VM_H

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Opcodes
#define OP_PUSH         0x01
#define OP_POP          0x02
#define OP_DUP          0x03

#define OP_ADD          0x10
#define OP_SUB          0x11
#define OP_MUL          0x12

#define OP_LOAD         0x20
#define OP_STORE        0x21

#define OP_JMP          0x30
#define OP_JZ           0x31
#define OP_CALL         0x32
#define OP_RET          0x33

#define OP_PRINT        0x40
#define OP_GETINT       0x41

#define OP_DUMP_REGS    0xE0
#define OP_DUMP_STACK   0xE1
#define OP_TRIGGER_ERROR 0xF0
#define OP_HALT         0xFF

// VM Structure
typedef struct VM {
    uint8_t memory[512];           // General purpose memory
    uint64_t stack[128];           // Operand stack
    size_t sp;                     // Stack pointer
    
    uint64_t call_stack[16];       // Return address stack - VULNERABLE!
    size_t call_sp;                // Call stack pointer
    
    uint64_t registers[8];         // General purpose registers
    size_t pc;                     // Program counter
    uint8_t *bytecode;             // Loaded program
    size_t bytecode_size;
    
    void (*error_handler)(struct VM*);  // Function pointer - TARGET!
    int exit_code;
    int halted;
} VM;

// Function declarations
VM* vm_init(uint8_t *bytecode, size_t size);
void vm_execute(VM *vm);
void vm_free(VM *vm);
void default_error_handler(VM *vm);

// Helper functions
uint8_t read_u8(VM *vm);
uint16_t read_u16(VM *vm);
uint64_t read_u64(VM *vm);
void push(VM *vm, uint64_t val);
uint64_t pop(VM *vm);

#endif
