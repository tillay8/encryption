package main

import (
	"fmt"
	"log"
	"os"
	"pgpcli/internal/createkey"
	"pgpcli/internal/decrypt"
	"pgpcli/internal/encrypt"
	"pgpcli/internal/export"
	"pgpcli/internal/importkey"
)

func main() {
    if len(os.Args) < 2 {
        fmt.Println(`./pgpcli create            creates a key
./pgpcli import            imports a key from clipboard
./pgpcli export <filepath> exports key to a file
./pgpcli encrypt           encrypt a message
./pgpcli decrypt           decrypts a message from clipboard`)
        log.Fatal("No argument provided")
    }
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
    case "import":
        err := importkey.ImportKey()
        if err != nil {
            log.Fatal(err)
        }
    case "decrypt":
        err := decrypt.Decrypt()
        if err != nil {
            log.Fatal(err)
        }
    case "export":
        if len(os.Args) < 3 {
            log.Fatal("Put in a filepath silly!")
        }
        err := export.Export(os.Args[2])
        if err != nil {
            log.Fatal(err)
        }
    }
}
