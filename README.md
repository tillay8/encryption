# encryption
Source code for all of the end to end encryption projects I have been doing with some friends

required dependencies
xclip, wl-clipboard, python-pyrcyptodome

default location for stored password is /tmp/key, which is wiped on reboot

can be changed my modifying the source code for encrypt.py

the python script automatically checks for whats on your clipboard

if it starts with `&&` it parses it as encrypted text

if it starts with `@@` it makes it the new password

if it starts with neither, it prompts the user for text to encrypt

support is best on linux, but windows sorta works (thanks novato)

theres also some stuff for using pgp keys for sharing passwords between people securel
