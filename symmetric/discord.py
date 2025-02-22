import json, os, http.client, sys, csv
from utils import encrypt, decrypt

os.system("mkdir -p ~/tilcord")

PASSWORD_FILE = "/tmp/key"
TOKEN_FILE = os.path.expanduser("~/tilcord/token")
CHANNEL_FILE = os.path.expanduser("~/tilcord/channel")
USERS_FILE = os.path.expanduser("~/tilcord/users.csv")

colors = [
    ("black", "\033[30m"), ("dark_red", "\033[31m"), ("green", "\033[32m"),
    ("dark_yellow", "\033[33m"), ("dark_blue", "\033[34m"), ("purple", "\033[35m"),
    ("teal", "\033[36m"), ("light_gray", "\033[37m"),
    ("dark_gray", "\033[90m"), ("red", "\033[91m"), ("lime", "\033[92m"),
    ("yellow", "\033[93m"), ("blue", "\033[94m"), ("magenta", "\033[95m"),
    ("cyan", "\033[96m"), ("white", "\033[97m"),
]

def get_pass():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            return f.read()

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
           return f.readline().strip()

def get_channel():
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, 'r') as f:
           return f.readline().strip()

header_data = {
    "Content-Type": "application/json",
    "User-Agent": "Discordbot",
    "Authorization": get_token()
}

def get_user_color(user):
    user_map = {}
    try:
        with open(USERS_FILE, mode='r') as file:
            for row in csv.reader(file):
                if len(row) == 2:
                    user_map[row[0].strip()] = row[1].strip()
    except FileNotFoundError:
        print("Please add a users.csv file\nFormat is like:\nuser1, red\nuser2, green\nuser3, yellow\netc")
        sys.exit(1)
    color_name = user_map.get(user)
    if color_name:
        return next(c[1] for c in colors if c[0] == color_name)
    return colors[-1][1]

def send_message(channel_id, message_content):
    conn = http.client.HTTPSConnection("discord.com", 443)
    message_data = json.dumps({
        "content": message_content,
        "tts": False
    })
    try:
        conn.request("POST", f"/api/v10/channels/{channel_id}/messages", message_data, header_data)
        response = conn.getresponse()

        if 199 < response.status < 300:
            print("Message sent successfully.")
            os.system("sleep 0.5&&clear")
        else:
            if response.status == 400:
                print(f"please add a channel file in {CHANNEL_FILE} :)\nthat can be specified by typing set <channel id>")
            else:
                print(f"Discord aint happy: {response.status} error")
    except TypeError as e:
        print(f"Please move your token file to {TOKEN_FILE}")
        sys.exit(1)
    finally:
        conn.close()

def listen_message(channel_id):
    conn = http.client.HTTPSConnection("discord.com", 443)
    try:
        conn.request("GET", f"/api/v10/channels/{channel_id}/messages", headers=header_data)
        response = conn.getresponse()
        if 199 < response.status < 300:
            messages = json.loads(response.read().decode())
            messages.reverse()
            prev_message = ""
            for message in messages[-1:]:
                if prev_message != message['content']:
                    if "&&" in message['content'] and message['content'] != None:
                        return f"{get_user_color(message['author']['username'])}{message['author']['username']}\033[0m: {decrypt(message['content'], get_pass())}"
                        prev_message = message['content']
        else:
            return(f"Discord aint happy: {response.status} error")
    except TypeError as e:
        print(f"Please move your token file to {TOKEN_FILE}\nyou could have also attempted to send a message that was too long")
        sys.exit(1)
    finally:
        conn.close()

try:
    os.system("clear")
    if sys.argv[1] == "listen":
        last_var = None
        while True:
            var = listen_message(get_channel())
            if var != last_var:
                if var != None:
                    print(var)
                    last_var = var
                else:
                    print(f"{colors[7][1]}[some unencrypted messages]")
                    last_var = None
    elif sys.argv[1] == "send":
        while True:
            to_send = input("Message to send: ")
            if to_send.startswith("set "):
                with open("channel_file.txt", 'w') as f:
                    f.write(to_send.split(" ", 1)[1])
            elif to_send.startswith("adduser "):
                words = to_send.split(" ", 1)[1].split(", ")
                if len(words) == 2 and any(words[1] == color[0] for color in colors):
                    with open(USERS_FILE, 'a') as f:
                        f.write(f"{words[0]}, {words[1]}\n")
                    print(f"added {words[0]}, {words[1]} to {USERS_FILE}")
            else:
                encrypted_message = encrypt(to_send, get_pass())
                send_message(get_channel(), "&&" + encrypted_message)
except KeyboardInterrupt:
    os.system("pkill tmux")
    os.system("clear")
