import os

# path
BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..", "..")))

FOLDERS = os.path.join(BASE_DIR, "folders")
SERVER_FOLDER = os.path.join(FOLDERS, "server")
GAME_META_FILE = os.path.join(SERVER_FOLDER, "games.csv")
LOCAL_GAME_META_FILE = os.path.join(BASE_DIR, "games.csv")
USER_DATA = os.path.join(SERVER_FOLDER, "user_datas.csv")


# Status definitions
UNLOGIN = "unlogin"
IDLE = "idle"
GAME_DEVOPLOP = "game develop"
INVITE_MANAGE = "invite manage"
IN_PRIVATE = "In Room private"
IN_PUBLIC = "In Room public"
HOST = "In Game host"
JOINER = "In Game joiner"
EXIT = "exit"

# Helper function for room status
def IN_ROOM_(room_type):
    return f"In Room {room_type}"


