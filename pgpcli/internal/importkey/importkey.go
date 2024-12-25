package importkey

import (
	"fmt"
	"os"

	"github.com/ProtonMail/gopenpgp/v3/crypto"
	"golang.design/x/clipboard"
)

func ImportKey() error {
    err := clipboard.Init()
    if err != nil {
        return err
    }
    clipboardBytes := clipboard.Read(clipboard.FmtText)
    clipText := string(clipboardBytes)

    _, err = crypto.NewKeyFromArmored(clipText)
    if err != nil {
        return err
    }

    fmt.Println("Enter username (remember this, its case sensitive!):")
    var user string
    fmt.Scan(&user)

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

    return nil
}
