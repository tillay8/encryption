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

random-password creates a random new password that starts with `@@` and can be run

support is best on linux, ~~but windows sorta works~~ windows support too hard to maintain

for sharing passwords between people securely just use kleopatra and pgp keys lmao
