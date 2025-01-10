package importkey

import (
	"fmt"
	"os"
	"pgpcli/lib/clipboard"

	"github.com/ProtonMail/gopenpgp/v3/crypto"
)

func ImportKey() error {
    clipText, err := clipboard.Read()
    if err != nil {
        return err
    }

    thisKey, err := crypto.NewKeyFromArmored(clipText)
    if err != nil {
        return err
    }

    user := "";
    for _, v := range thisKey.GetEntity().Identities {
        if user != "" {
            break
        }
        user = trimToFirstWord(v.Name)
    }
    fmt.Println("User: " + user)

    homeDir, err := os.UserHomeDir()
    if err != nil {
        return err
    }

    _, err = os.Stat(homeDir + "/wpgp/" + user + ".pub")
    if !(os.IsNotExist(err)) {
        os.Remove(homeDir + "/wpgp/" + user + ".pub")
    }
    pubKeyFile, err := os.Create(homeDir + "/wpgp/" + user + ".pub")
    if err != nil {
        return err
    }
    defer pubKeyFile.Close()
    pubKeyString := clipText
    if err != nil {
        return err
    }
    _, err = pubKeyFile.WriteString(pubKeyString)
    if err != nil {
        return err
    }

    err = clipboard.Write("")
    if err != nil {
        return err
    }

    fmt.Println("successful key import")

    return nil
}

func trimToFirstWord(x string) string {
    for i := 0; i < len(x); i++ {
        if string(x[i]) == " " {
            x = x[:i]
            break;
        }
    }

    return x
}
