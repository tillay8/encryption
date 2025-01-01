package createkey

import (
	"fmt"
	"os"

	"github.com/ProtonMail/gopenpgp/v3/constants"
	"github.com/ProtonMail/gopenpgp/v3/crypto"
	"github.com/ProtonMail/gopenpgp/v3/profile"
)

func CreateKey() error {
    pgp := crypto.PGP()

    fmt.Println("Enter the key's passphrase:")
    var v string;
    fmt.Scan(&v)
    passphrase := []byte(v)

    keygenhandle := crypto.PGPWithProfile(profile.RFC9580()).KeyGeneration().AddUserId("createdwithwpgp", "nowhere@goesnowhere.com").New()
    privKey, err := keygenhandle.GenerateKeyWithSecurity(constants.HighSecurity)
    if err != nil {
        return err
    }
    lockedKey, err := pgp.LockKey(privKey, passphrase)
    if err != nil {
        return err
    }

    homeDir, err := os.UserHomeDir()
    if err != nil {
        return err
    }

    _, err = os.Stat(homeDir + "/wpgp")
    if os.IsNotExist(err) {
        err = os.Mkdir(homeDir + "/wpgp", 0755)
        if err != nil {
            return err
        }
    }
    err = os.Chmod(homeDir + "/wpgp", 0755)
    if err != nil {
        return err
    }

    _, err = os.Stat(homeDir + "/wpgp/MAINKEY")
    if !(os.IsNotExist(err)) {
        os.Remove(homeDir + "/wpgp/MAINKEY")
    }
    keyFile, err := os.Create(homeDir + "/wpgp/MAINKEY")
    if err != nil {
        return err
    }
    defer keyFile.Close()
    keyString, err := lockedKey.Armor()
    if err != nil {
        return err
    }
    _, err = keyFile.WriteString(keyString)
    if err != nil {
        return err
    }

    _, err = os.Stat(homeDir + "/wpgp/MAINKEY.pub")
    if !(os.IsNotExist(err)) {
        os.Remove(homeDir + "/wpgp/MAINKEY.pub")
    }
    pubKeyFile, err := os.Create(homeDir + "/wpgp/MAINKEY.pub")
    if err != nil {
        return err
    }
    defer pubKeyFile.Close()
    pubKeyString, err := privKey.GetArmoredPublicKey()
    if err != nil {
        return err
    }
    _, err = pubKeyFile.WriteString(pubKeyString)
    if err != nil {
        return err
    }

    fmt.Println("New key created as " + pubKeyFile.Name() + ". Export it with ./pgpcli export ./myfile")

    return nil
}
