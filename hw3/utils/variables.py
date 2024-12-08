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
INVITE_SENDING = "invite sending"
IN_ROOM_HOST = "In Room Host"
IN_ROOM_PLAYER = "In Room player"
IN_ROOM = "In Room"
IN_GAME_HOST = "In Game host"
IN_GAME_PLAYER = "In Game player"
IN_GAME = "In Game"
EXIT = "exit"


# Helper function for room status
def IN_ROOM_(room_type):
    return f"In Room {room_type}"

Room_list = ["private", "public"]
