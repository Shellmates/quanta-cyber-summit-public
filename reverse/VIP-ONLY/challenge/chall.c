/*
    compiling : gcc -static -s chall.c -o chall
*/

#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<stdint.h>
#include<unistd.h>
#include <sys/ptrace.h>


const uint8_t ENCRYPTED_FLAG[0x3f] = {    
    0x74, 0x6a, 0x7f, 0x70, 0x80, 0x6d, 0x73, 0x93, 0x7c, 0x81, 0x8d, 0x55,
    0x49, 0x86, 0x55, 0x71, 0x75, 0x4a, 0x83, 0x57, 0x73, 0x44, 0x87, 0x83,
    0x5c, 0x6d, 0x73, 0x6d, 0x6e, 0x59, 0x60, 0x71, 0x4a, 0x70, 0x70, 0x4d,
    0x88, 0x33, 0x71, 0x67, 0x5c, 0x6d, 0x5b, 0x32, 0x77, 0x44, 0x6f, 0x64,
    0x66, 0x58, 0x4d, 0x76, 0x38, 0x49, 0x60, 0x66, 0x76, 0x70, 0x45, 0x6f,
    0x3c, 0x64, 0x8d
};

bool catchDebugger(){
    if (ptrace(PTRACE_TRACEME, 0, 1, 0) < 0) {
        return true;
    }
    ptrace(PTRACE_DETACH, 0, 1, 0);
    return false;
}


void generateSecretKey(uint8_t *secret_key){

    char *environ_key = getenv("KEY");

    if (environ_key == NULL){
        puts("An Error occured :(");
        exit(1);
    }
    
    for (int i = 0 ; i<0x10  ; i++){
        secret_key[i] = (uint8_t)environ_key[i] ^ i ^ 0x51 ;
    }
    
}

int checkEnvKey() {

    int a = 13 ;
    int b = 37 ;

    uint8_t target[16] = {
        0x10, 0x4f, 0xff, 0xcd, 0xe1, 0xfd, 0x5f, 0xb8,
        0x1e, 0xab, 0x27, 0xdb, 0x3d, 0xbd, 0x09, 0x07
    };

    char* e = getenv("KEY");

    if (e == NULL || strlen(e) != 16) return 0;
    else {

        for (int i = 0 ; i < 16 ; i++){
            uint8_t s[16];
            s[i] = (a * (uint8_t)e[i] + b * i ) % 256;

            if (s[i] != target[i]){
                return 0;
            }
        }

        return 1;
    }   
}

void fun(uint8_t *data , uint8_t  *secret_key , uint8_t *output , int len_data , int len_key )
{
    for (int i = 0 ; i < len_data ; i++ ){
        output[i] = (data[i] + secret_key[i % len_key]) % 256;
    }

}



int main(){

    uint8_t password[100];
    uint8_t encryption_key[16];

    puts("Welcome player before having fun i need to check something first ^_^");
    sleep(3);
    int x = checkEnvKey();
    if (x != 1 ){
        puts("sorry looks like you're not invited lololololol");
        exit(1);
    }

    else {
        printf("Oh wow that was unexepected lol let me check something else and let the fun begin\n");
        sleep(2);

        if (catchDebugger()){
            puts("\nSorryyyyy you did something that we cannot tolerate goodbye ");
            exit(1);
        }

        printf("give me the pass >> ");
        fgets(password, sizeof(password), stdin);
        password[strcspn(password, "\n")] = 0;

        if (strlen(password) != 0x3f){
            puts("not quite my length , ADIOS :/");
            exit(1);
        }

        generateSecretKey(encryption_key);
        uint8_t output[0x3f];
        fun(password, encryption_key, output, 0x3f, 16);

        if (memcmp(&output, &ENCRYPTED_FLAG, 0x3f) == 0){
            puts("\nYOU'RE INNNNNNNNNNNN , you're a VIP member now");
        } else {
            puts("\nYou're an imposter we cant let you in");
            exit(1);
        }
    }
} 