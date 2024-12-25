package decrypt

import (
	"fmt"
	"pgpcli/internal/keyutils"

	"github.com/ProtonMail/gopenpgp/v3/crypto"
	"golang.design/x/clipboard"
)

func Decrypt() error {
    err := clipboard.Init()
    if err != nil {
        return err
    }
    clipboardBytes := clipboard.Read(clipboard.FmtText)
    clipText := string(clipboardBytes)

    fmt.Println("Enter key passphrase:")
    var passphraseBytes string
    fmt.Scan(&passphraseBytes)
    passphrase := string(passphraseBytes)

    privKey, err := keyutils.GetMainPrivKey(passphrase)
    if err != nil {
        return err
    }

    pgp := crypto.PGP()
    decHandle, err := pgp.Decryption().DecryptionKey(&privKey).New()
    decrypted, err := decHandle.Decrypt([]byte(clipText), crypto.Armor)
    myMessage := string(decrypted.Bytes())

    fmt.Println(myMessage)

    return nil
}
