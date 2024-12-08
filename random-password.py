import random, string, os, subprocess

length = 30
characters = string.ascii_letters + string.digits + string.punctuation
password = (''.join(random.choices(characters, k=length)))

try:
    if "WAYLAND_DISPLAY" in os.environ: 
        subprocess.run(["wl-copy"], input=password, text=True, check=True)
    elif "DISPLAY" in os.environ:
        subprocess.run(["xclip", "-selection", "clipboard"], input=password, text=True, check=True)
except Exception as e:
    print("ERRORRRR: skill issue")

print("password copied to clip")
