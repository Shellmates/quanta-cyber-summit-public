#include "vm.h"

void default_error_handler(VM *vm) {
    fprintf(stderr, "VM Error at PC=%lu\n", vm->pc);
    vm->halted = 1;
    vm->exit_code = 1;
}

VM* vm_init(uint8_t *bytecode, size_t size) {
    VM *vm = (VM*)malloc(sizeof(VM));
    if (!vm) return NULL;
    
    memset(vm, 0, sizeof(VM));
    vm->bytecode = bytecode;
    vm->bytecode_size = size;
    vm->error_handler = default_error_handler;
    vm->sp = 0;
    vm->call_sp = 0;
    vm->pc = 0;
    vm->halted = 0;
    vm->exit_code = 0;
    
    return vm;
}

void vm_free(VM *vm) {
    if (vm) {
        if (vm->bytecode) free(vm->bytecode);
        free(vm);
    }
}

uint8_t read_u8(VM *vm) {
    if (vm->pc >= vm->bytecode_size) {
        vm->error_handler(vm);
        return 0;
    }
    return vm->bytecode[vm->pc++];
}

uint16_t read_u16(VM *vm) {
    if (vm->pc + 1 >= vm->bytecode_size) {
        vm->error_handler(vm);
        return 0;
    }
    uint16_t val = *(uint16_t*)(&vm->bytecode[vm->pc]);
    vm->pc += 2;
    return val;
}

uint64_t read_u64(VM *vm) {
    if (vm->pc + 7 >= vm->bytecode_size) {
        vm->error_handler(vm);
        return 0;
    }
    uint64_t val = *(uint64_t*)(&vm->bytecode[vm->pc]);
    vm->pc += 8;
    return val;
}

void push(VM *vm, uint64_t val) {
    if (vm->sp >= 128) {
        fprintf(stderr, "Stack overflow!\n");
        vm->error_handler(vm);
        return;
    }
    vm->stack[vm->sp++] = val;
}

uint64_t pop(VM *vm) {
    if (vm->sp == 0) {
        fprintf(stderr, "Stack underflow!\n");
        vm->error_handler(vm);
        return 0;
    }
    return vm->stack[--vm->sp];
}

void vm_execute(VM *vm) {
    while (!vm->halted && vm->pc < vm->bytecode_size) {
        uint8_t opcode = read_u8(vm);
        
        switch(opcode) {
            case OP_PUSH: {
                uint64_t val = read_u64(vm);
                push(vm, val);
                break;
            }
            
            case OP_POP: {
                pop(vm);
                break;
            }
            
            case OP_DUP: {
                if (vm->sp == 0) {
                    vm->error_handler(vm);
                    break;
                }
                uint64_t val = vm->stack[vm->sp - 1];
                push(vm, val);
                break;
            }
            
            case OP_ADD: {
                uint64_t b = pop(vm);
                uint64_t a = pop(vm);
                push(vm, a + b);
                break;
            }
            
            case OP_SUB: {
                uint64_t b = pop(vm);
                uint64_t a = pop(vm);
                push(vm, a - b);
                break;
            }
            
            case OP_MUL: {
                uint64_t b = pop(vm);
                uint64_t a = pop(vm);
                push(vm, a * b);
                break;
            }
            
            case OP_LOAD: {
                uint16_t idx = read_u16(vm);
                // VULNERABILITY 3: Can read beyond memory for info leaks
                if (idx >= 512 && idx < 2048) {
                    fprintf(stderr, "Warning: Load from extended memory at %u\n", idx);
                }
                uint64_t val = *(uint64_t*)(&vm->memory[idx]);
                push(vm, val);
                break;
            }
            
            case OP_STORE: {
                uint16_t idx = read_u16(vm);
                uint64_t val = pop(vm);
                // VULNERABILITY 2: Limited bounds check
                // Allows some overflow but not arbitrary writes
                if (idx >= 512 && idx < 2048) {
                    // Warning but still executes - can overflow into VM struct!
                    fprintf(stderr, "Warning: Store to extended memory at %u\n", idx);
                }
                *(uint64_t*)(&vm->memory[idx]) = val;
                break;
            }
            
            case OP_JMP: {
                uint16_t addr = read_u16(vm);
                vm->pc = addr;
                break;
            }
            
            case OP_JZ: {
                uint16_t addr = read_u16(vm);
                uint64_t val = pop(vm);
                if (val == 0) {
                    vm->pc = addr;
                }
                break;
            }
            
            case OP_CALL: {
                uint16_t addr = read_u16(vm);
                // VULNERABILITY: No bounds check on call_sp!
                // call_stack is only 16 entries, but we never check if call_sp >= 16
                vm->call_stack[vm->call_sp++] = vm->pc;
                vm->pc = addr;
                break;
            }
            
            case OP_RET: {
                // VULNERABILITY: No underflow check!
                if (vm->call_sp == 0) {
                    fprintf(stderr, "Call stack underflow\n");
                    vm->error_handler(vm);
                    break;
                }
                vm->pc = vm->call_stack[--vm->call_sp];
                break;
            }
            
            case OP_PRINT: {
                uint64_t val = pop(vm);
                printf("%lu\n", val);
                break;
            }
            
            case OP_GETINT: {
                uint64_t val;
                if (scanf("%lu", &val) == 1) {
                    push(vm, val);
                } else {
                    push(vm, 0);
                }
                break;
            }
            
            case OP_DUMP_REGS: {
                printf("=== Register Dump ===\n");
                for (int i = 0; i < 8; i++) {
                    printf("R%d: 0x%016lx\n", i, vm->registers[i]);
                }
                printf("PC: 0x%016lx\n", vm->pc);
                printf("SP: %lu\n", vm->sp);
                printf("Call SP: %lu\n", vm->call_sp);
                break;
            }
            
            case OP_DUMP_STACK: {
                printf("=== Stack Dump ===\n");
                printf("Stack pointer: %lu\n", vm->sp);
                for (size_t i = 0; i < vm->sp && i < 10; i++) {
                    printf("[%lu]: 0x%016lx\n", i, vm->stack[i]);
                }
                if (vm->sp > 10) {
                    printf("... (%lu more entries)\n", vm->sp - 10);
                }
                break;
            }
            
            case OP_TRIGGER_ERROR: {
                vm->error_handler(vm);
                break;
            }
            
            case OP_HALT: {
                vm->halted = 1;
                break;
            }
            
            default: {
                fprintf(stderr, "Unknown opcode: 0x%02x at PC=%lu\n", opcode, vm->pc - 1);
                vm->error_handler(vm);
                break;
            }
        }
        
        if (vm->halted) break;
    }
}
