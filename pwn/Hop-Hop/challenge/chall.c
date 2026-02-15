// ../compile/build.sh
#define _GNU_SOURCE
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <seccomp.h>

__asm__(
    "pop %rdi;\n"
    "ret;\n"
);

void setup(){
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0); 
    setvbuf(stderr, NULL, _IONBF, 0);
}

int main(int argc, char const *argv[]){
    char buffer[0x40];
    
    setup();

    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ALLOW);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(execve), 0) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(execveat), 0) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(open), 0) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(fork), 0) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(mprotect), 0) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(mmap), 0) == 0);
    
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(read), 1, SCMP_A0(SCMP_CMP_NE, 0)) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(pread64), 0) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(readv), 0) == 0);

    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(write), 1, SCMP_A0(SCMP_CMP_NE, 1)) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(pwrite64), 0) == 0);
    assert(seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(writev), 0) == 0);
    
    assert(seccomp_load(ctx) == 0);

    puts("Hop Hop little bunny, I am coming to eat you");
    puts("Hop Hop little bunny, I am coming to kill you\n");

    printf("What will you do? what CAN you do? ");

    fgets(buffer, 0x160, stdin);

    return 0;
}