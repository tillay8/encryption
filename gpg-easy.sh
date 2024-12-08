#!/bin/bash

choice=$(gum choose "create key" "import key" "encrypt message" "decrypt message")

case "$choice" in
"create key")
    gpg --gen-key
    ;;
"import key")
    read -rp "Enter the file name to import: " import_file
    gpg --armor --import "$import_file"
    ;;
"encrypt message")
    read -rp "Enter the text to encrypt: " text
    echo "Enter recipient names (type 'q' to finish):"
    recipients=()
    while read -rp "Recipient: " recipient && [ "$recipient" != "q" ]; do
        recipients+=("--recipient" "$recipient")
    done
    encrypted_text=$(echo "$text" | gpg --sign --armor --encrypt "${recipients[@]}" 2>/dev/null)
    echo "$encrypted_text" | wl-copy --type text/plain
    echo "Encrypted text has been copied to the clipboard."
    ;;
"decrypt message")
    if wl-paste | grep -q "BEGIN PGP MESSAGE"; then
        decrypted_text=$(wl-paste | gpg --armor --decrypt 2>/dev/null)
        if [ $? -eq 0 ]; then
            print "$decrypted_text" | wl-copy --type text/plain
            echo "Decrypted text has been copied to the clipboard."
        else
            echo "Decryption failed."
        fi
    else
        echo "No PGP message found in the clipboard."
    fi
    ;;
*)
    echo "Invalid choice."
    ;;
esac
