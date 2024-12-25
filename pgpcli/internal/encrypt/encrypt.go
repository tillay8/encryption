package encrypt

import (
	"fmt"
	"pgpcli/internal/keyutils"

	"github.com/ProtonMail/gopenpgp/v3/crypto"
)

func Encrypt() error {
    fmt.Println("Encrypted message:")
    var v string
    fmt.Scan(&v)

    pgp := crypto.PGP()

    keyring, err := crypto.NewKeyRing(nil)
    if err != nil {
        return err
    }

    for {
        var next string
        fmt.Println("Name of next recipient, or type HALT:")
        fmt.Scan(&next)
        if next == "HALT" {
            break
        }
        nextKey, err := keyutils.GetPubKeyOfUser(next)
        if err != nil {
            return err
        }
        keyring.AddKey(&nextKey)
    }
    encHandle, err := pgp.Encryption().Recipients(keyring).New()

    pgpMessage, err := encHandle.Encrypt([]byte(v))
    armored, err := pgpMessage.Armor()

    fmt.Println(armored)
    return nil
}
