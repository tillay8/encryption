package export

import (
	"io"
	"os"
)

func Export(filename string) error {
    homeDir, err := os.UserHomeDir()
    if err != nil {
        return err
    }

    src, err := os.Open(homeDir + "/wpgp/MAINKEY.pub")
    if err != nil {
        return err
    }
    defer src.Close()

    // Create destination file
    dst, err := os.Create(filename)
    if err != nil {
        return err
    }
    defer dst.Close()

    // Copy source to destination
    _, err = io.Copy(dst, src)
    if err != nil {
        return err
    }

    return nil
}
