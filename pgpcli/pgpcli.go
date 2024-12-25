package main

import (
	"log"
	"os"
	"pgpcli/internal/createkey"
	"pgpcli/internal/encrypt"
)

func main() {
    action := os.Args[1]

    switch action {
    case "create":
        err := createkey.CreateKey()
        if err != nil {
            log.Fatal(err)
        }
    case "encrypt":
        err := encrypt.Encrypt()
        if err != nil {
            log.Fatal(err)
        }
    }
}
