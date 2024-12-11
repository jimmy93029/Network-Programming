import os

# path
BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..", "..")))
FOLDERS = os.path.join(BASE_DIR, "folders")
SERVER_FOLDER = os.path.join(FOLDERS, "server")
LOCAL_GAME_META_FILE = os.path.join(os.getcwd(), "games.csv")
USER_DATA = os.path.join(os.getcwd(), "user_datas.csv")

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

# Data structures : Room 
NAME = "name"
HOST = "host"
GAME = "game"
STATUS = "status"
ROOM_TYPE = "room type"
PLAYERS = "players"
WAITING = "waiting"
MAX_PLAYERS = 1

# Data structures : invitations 
MESSAGE = "message"

# Data structures : online users
ADDRESS = "address"
SOCKET = "socket"

# File structures : games.csv
GAME_NAME = "game_name"
DEVEPLOPER = "developer"
INTRO = "introduction"
VERSION = "version"
