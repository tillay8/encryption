function create () {
    clear
    gpg --gen-key
}

function toclipboard () {
    if [ $(loginctl show-session $(awk '/tty/ {print $1}' <(loginctl)) -p Type | awk -F= '{print $2}') == "x11" ]; then
        echo $toclipboard | xclip -selection clipboard
    elif [ $(loginctl show-session $(awk '/tty/ {print $1}' <(loginctl)) -p Type | awk -F= '{print $2}') == "wayland" ]; then
        echo $toclipboard | wl-copy
    fi
}

function fromclipboard () {
    if [ $(loginctl show-session $(awk '/tty/ {print $1}' <(loginctl)) -p Type | awk -F= '{print $2}') == "x11" ]; then
        fromclipboard=$(xclip -o -selection clipboard)
    elif [ $(loginctl show-session $(awk '/tty/ {print $1}' <(loginctl)) -p Type | awk -F= '{print $2}') == "wayland" ]; then
        fromclipboard=$(wl-paste)
    fi
}

function import () {
    touch /tmp/westorekeyshere.gpg
    rm /tmp/westorekeyshere.gpg
    echo $fromclipboard >> /tmp/westorekeyshere.gpg
    gpg --import /tmp/westorekeyshere.gpg
}

choice=$(gum choose "create-key" "import" "encrypt" "decrypt")
case "$choice" in
"create-key")
    create
    ;;
"import")
    fromclipboard
    echo $fromclipboard
    import
    ;;
"export")
    ;;
"encrypt")
    ;;
"decrypt")
    ;;
esac
