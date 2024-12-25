package main

import (
	"log"
	"os"
	"pgpcli/internal/createkey"
	"pgpcli/internal/decrypt"
	"pgpcli/internal/encrypt"
	"pgpcli/internal/export"
	"pgpcli/internal/importkey"
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
        if os.Args[2] == "" {
            log.Fatal("Put in a filepath silly!")
        }
        err := export.Export(os.Args[2])
        if err != nil {
            log.Fatal(err)
        }
    }
}
