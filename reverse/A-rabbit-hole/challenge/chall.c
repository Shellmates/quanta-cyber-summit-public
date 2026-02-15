/* 
    compiling : gcc -s chall.c -o challenge
*/
#include<stdio.h>
#include<string.h>
#include<stdint.h>

const unsigned int key[] = {0x62,0x75,0x67,0x73,0x62,0x75,0x6e,0x6e,0x79};
const int key_len = 0x9;

void encrypt1(unsigned int *data , const unsigned int *key , int data_len , int key_len){
    for(int i = 0 ; i < data_len ; i++){
        data[i] ^= key[i % key_len];
    }
}

void encrypt2(unsigned int *data , int data_len){
    for(int i = 0 ; i < data_len ; i++){
        if (data[i] % 2 == 0){
            data[i] = (data[i] + i ) % 256;
        }
        else {
            data[i] = (data[i] - i) % 256;
        }
    }
}

void encrypt3(unsigned int *data , int data_len) {
    for(int i = 0 ; i < data_len ; i++){
        data[i] ^= i; 
    }
}

void encrypt4(unsigned int *data , int data_len){
    for(int i = 0 ; i < data_len ; i++){
        data[i] = data[i] ^ (data[i] >> 1);
    }
}



int main (void){
    unsigned int input[256];
    printf("Give me your input dude :))))) : ");
    char temp[256];
    scanf("%255s" , temp);
    int len = strlen(temp);
    for(int i = 0; i < len; i++) {
        input[i] = (unsigned int)temp[i];
    }
    encrypt1(input , key , len , key_len);
    encrypt2(input , len);
    encrypt3(input , len);
    encrypt4(input , len);

    FILE *outfile ; 
    outfile = fopen("output.enc" , "wb");
    if (outfile == NULL){
        printf("Error opening file\n");
        return 1;
    }
    for(int i = 0; i < len; i++) {
        fprintf(outfile , "%02x" , input[i]);
    }
    fclose(outfile);
    
}