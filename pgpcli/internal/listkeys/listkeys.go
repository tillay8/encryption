package listkeys

import (
	"fmt"
	"os"
)

func ListKeys() error {
    homeDir, err := os.UserHomeDir()
    if err != nil {
        return err
    }

    entries, err := os.ReadDir(homeDir + "/wpgp/")
    if err != nil {
        return err
    }

    for _, e := range entries {
        if (e.Name() != "MAINKEY") {
            fmt.Println(e.Name())
        }
    }

    return nil
}
