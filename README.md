# encryption
Source code for all of the end to end encryption projects I have been doing with some friends

required dependencies:

`xclip, wl-clipboard, python-pyrcyptodome`

default location for stored password is /tmp/key, which is wiped on reboot because its in ram

can be changed my modifying the source code for encrypt.py

the python script automatically checks for whats on your clipboard

if it starts with `&&` it parses it as encrypted text

if it starts with `@@` it makes it the new password

if it starts with neither, it prompts the user for text to encrypt

flags: 

`-p`: create new password, overwrite current saved password with it, and copy the new one to the clipboard

`-n`: manually type in a new password

support is only for linux with x11 or wayland

for sharing passwords between people securely just use pgp keys
