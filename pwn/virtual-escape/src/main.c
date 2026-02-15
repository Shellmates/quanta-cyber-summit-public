#include "vm.h"

void win() {
    printf("\n🎉 Congratulations! You've exploited the VM! 🎉\n\n");
    system("cat flag.txt 2>/dev/null || echo 'flag{test_flag_replace_in_production}'");
    exit(0);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <bytecode_file>\n", argv[0]);
        return 1;
    }
    
    // Read bytecode from file
    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", argv[1]);
        return 1;
    }
    
    // Get file size
    fseek(f, 0, SEEK_END);
    size_t size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    if (size == 0) {
        fprintf(stderr, "Error: Empty bytecode file\n");
        fclose(f);
        return 1;
    }
    
    // Allocate and read bytecode
    uint8_t *bytecode = (uint8_t*)malloc(size);
    if (!bytecode) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        fclose(f);
        return 1;
    }
    
    if (fread(bytecode, 1, size, f) != size) {
        fprintf(stderr, "Error: Failed to read bytecode\n");
        free(bytecode);
        fclose(f);
        return 1;
    }
    fclose(f);
    
    printf("ByteForge VM v1.0\n");
    printf("Loaded %lu bytes of bytecode\n", size);
    printf("Starting execution...\n\n");
    
    // Initialize and execute VM
    VM *vm = vm_init(bytecode, size);
    if (!vm) {
        fprintf(stderr, "Error: VM initialization failed\n");
        free(bytecode);
        return 1;
    }
    
    vm_execute(vm);
    
    int exit_code = vm->exit_code;
    vm_free(vm);
    
    printf("\nVM halted with exit code: %d\n", exit_code);
    return exit_code;
}
