package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"fmt"
	mrand "math/rand"
	"os"
)

func generateRandomIv() []byte {
	a := mrand.Intn(10)
	b := mrand.Intn(10)
	c := mrand.Intn(10)
	d := mrand.Intn(10)
	iv := fmt.Sprintf("%d%d%d%d", a, b, c, d)
	iv = string(iv) + string(iv) + string(iv) + string(iv)
	return []byte(iv)
}

func pkcs7Pad(data []byte, blockSize int) []byte {
	padding := blockSize - len(data)%blockSize
	padText := bytes.Repeat([]byte{byte(padding)}, padding)
	return append(data, padText...)
}

func encrypt(key, plaintext []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	plaintext = pkcs7Pad(plaintext, aes.BlockSize)
	ciphertext := make([]byte, aes.BlockSize+len(plaintext))
	iv := generateRandomIv()
	copy(ciphertext[:aes.BlockSize], iv)

	mode := cipher.NewCBCEncrypter(block, iv)
	mode.CryptBlocks(ciphertext[aes.BlockSize:], plaintext)

	return ciphertext, nil
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: ./main <Input>")
		os.Exit(1)
	}
	plaintext := os.Args[1]
	key := []byte("1337133713371337")
	ciphertext, err := encrypt(key, []byte(plaintext))
	if err != nil {
		os.Exit(1)
	}
	os.WriteFile("encrypted.bin", ciphertext, 0644)
}
