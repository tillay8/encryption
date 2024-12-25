# encryption
Source code for all of the end to end encryption projects I have been doing with some friends

required dependencies:

`xclip, wl-clipboard, python-pyrcyptodome, tk, python-pillow`

# Usage 

The default location for stored password is /tmp/key, which is wiped on reboot because its in ram.

This can be changed my modifying the source code for encrypt.py

The python script automatically checks for whats on your clipboard:

- if it starts with `&&` it parses it as encrypted text

- if it starts with `@@` it makes it the new password

- if it starts with `££` it parses it as an encrypted image

- if it is an png image, it encryptes the image (Other image types probably coming soonish maybe)

- if it starts with none of these, it prompts the user for text to encrypt

Flags:

- `-p`: create new password, overwrite current saved password with it, and copy the new one to the clipboard. Add a number with the length of the password after

- `-n`: manually type in a new password

- `-i`: automatically opens a window with decrypted image for viewing

add the following line to your hyprland config to make the preview image floating:

`windowrule=float,title:^(Image)(.*)$`

support is only for Linux with X11 or Wayland (Windows is annoyying to code for)

For sharing passwords between people securely just use pgp keys.

decryptpgp.sh can take a PGP message on your clipboard and attempt to decrypt it if someone sends you a key

use a graphical asymetric encryption tool like kleopatra for more complicated encryption work



# Testing protocol:

For encrypt.py:

See what happens when you run the script with:

- Nothing on your clipboard (should prompt for text)

- Encrypted text from previous test

- Encrypted text already made on previous versions

- Decrypted PNG image

- Encrypted PNG image from previous test

- Encrypted PNG image from previous version

- Encrypted PNG image from short copy from discord

- Broken PNG image from attempted short copy from discord

- Encrypted PNG image from download button on discord (message.txt)

- Corrupted message.txt

- Password starting with password prefix

- Weird junk and file formats on clipboard

- `-p` flag (make new random password)

- `-n` flag (prompt manually for new password)

- `-i` flag (preview image after decyryption)

- packages `xclip, wl-clipboard, python-pyrcyptodome, tk` not installed

- Not on a Linux system

- On both Wayland and X11

- On a Linux system but no desktop environment (in tty)
