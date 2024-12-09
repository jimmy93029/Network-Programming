import os

# path
BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..", "..")))
FOLDERS = os.path.join(BASE_DIR, "folders")
SERVER_FOLDER = os.path.join(FOLDERS, "server")
GAME_META_FILE = os.path.join(SERVER_FOLDER, "games.csv")
LOCAL_GAME_META_FILE = os.path.join(BASE_DIR, "games.csv")
USER_DATA = os.path.join(SERVER_FOLDER, "user_datas.csv")


# Status 
UNLOGIN = "unlogin"
IDLE = "idle"
GAME_DEVOPLOP = "game develop"
INVITE_MANAGE = "invite manage"
INVITE_SENDING = "invite sending"
IN_ROOM_HOST = "In Room Host"
IN_ROOM_PLAYER = "In Room player"
IN_ROOM = "In Room"
IN_GAME_HOST = "In Game host"
IN_GAME_PLAYER = "In Game player"
IN_GAME = "In Game"
EXIT = "exit"
PRIVATE = "private"
PUBLIC = "public"
Room_list = [PRIVATE , PUBLIC]

def IN_ROOM_(room_type):
    return f"In Room {room_type}"

# Room 
NAME = "name"
HOST = "host"
GAME = "game"
STATUS = "status"
ROOM_TYPE = "room type"
PLAYERS = "players"
WAITING = "waiting"

# invitations 
MESSAGE = "message"

# online users
ADDRESS = "address"
SOCKET = "socket"

# Data init
def server_init():
    os.makedirs(SERVER_FOLDER, exist_ok=True)
    print(f"Directories '{SERVER_FOLDER}' ensured to exist.")

    if not os.path.exists(GAME_META_FILE):
        with open(GAME_META_FILE, 'w') as f:
            pass  # Create an empty file

    if not os.path.exists(USER_DATA):
        with open(USER_DATA, 'w') as f:
            pass  # Create an empty file

def client_init():
    if not os.path.exists(LOCAL_GAME_META_FILE):
        with open(LOCAL_GAME_META_FILE, 'w') as f:
            pass  # Create an empty file

def user_init(username, online_users, client, mailbox, invitations, addr):
    online_users[username] = {STATUS: IDLE, SOCKET: client, ADDRESS:addr}
    mailbox[username] = []
    invitations[username] = {}