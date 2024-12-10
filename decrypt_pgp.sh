detect_clipboard_tool() {
  if command -v wl-paste &>/dev/null; then
    echo "wl-paste"
  elif command -v xclip &>/dev/null; then
    echo "xclip -selection clipboard -o"
  fi
}
clipboard_tool=$(detect_clipboard_tool)
clipboard_content=$(eval "$clipboard_tool")
if [[ "$clipboard_content" =~ -----BEGIN\ PGP\ MESSAGE----- && "$clipboard_content" =~ -----END\ PGP\ MESSAGE----- ]]; then
  decrypted_message=$(echo "$clipboard_content" | gpg --decrypt 2>/dev/null)
  if [ $? -eq 0 ]; then
    echo "$decrypted_message"
  fi
fi
