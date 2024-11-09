from utils.connection import connect_to_server
from utils.tools import selects_type
from .game1 import Tic_tac_toe
from .game2 import dark_chess

game_list = ["Tic_tac_toe", "dark_chess"]


"""Client A"""
def start_game1(client_socket, game_socket1, game_type):
    """
    房間創建者啟動遊戲伺服器，並處理遊戲邏輯。
    """
    print("Waiting for Player B to connect...")
    message = client_socket.recv(1024).decode()
    if message != "PlayerB connect successfully":
        print(message)
        return

    PleyerA, _ = game_socket1.accept()
    print("Player B connected.")

    # gaming
    if game_type == game_list[0]:
        Tic_tac_toe(PleyerA, "A")
    else:
        dark_chess(PleyerA, "A")

    # 通知遊戲結束
    client_socket.sendall(b"FINISH")
    game_socket1.close()


"""Client B"""
def start_game2(client_socket, game_addr, game_type):
    """
    房間加入者連接到遊戲伺服器，參與遊戲。
    """
    # try to connect ot game server
    try:
        print("Connecting to Game Server as Participant...")
        PlayerB = connect_to_server(game_addr)
        client_socket.sendall(f"START_GAME successfully".encode())

    except Exception as e:
        print(f"Error during game participation: {e}")
        retry(client_socket, game_addr, game_type)
        return
 
    # gaming
    if game_type == game_list[0]:
        Tic_tac_toe(PlayerB, "B")
    else:
        dark_chess(PlayerB, "B")

    PlayerB.close()


def retry(client_socket, game_addr, game_type):
    """
    提供房間加入者重新連接或退出選擇。
    """
    options = ["reconnect", "exit"]
    idx = selects_type("options", options)

    if options[idx] == "reconnect":
        start_game2(client_socket, game_addr, game_type)
    else:
        client_socket.sendall("START_GAME failed".encode())
        print("Exited the room.")


def handle_game_start(data, client, addr, rooms, login_addr, online_users):
    _, message = data.split()

    playerb = login_addr[addr]
    roomId = next((key for key, info in rooms.items() if info["participant"] == playerb), None)
    creator = rooms[roomId]["creator"]
    playera_socket = online_users[creator]["socket"]

    if message == "successfully":
        playera_socket.send(b"PlayerB connect successfully")
    else:
        playera_socket.send(b"PlayerB exit")


def handle_game_ending(data, client, addr, rooms, login_addr, online_users):

    playera = login_addr[addr]
    roomId = next((key for key, info in rooms.items() if info["creator"] == playera), None)
    playerb = rooms[roomId]["participant"]
    
    # change status 
    rooms.pop(roomId, None)
    online_users[playera]["status"] = "idle"
    online_users[playerb]["status"] = "idle"


