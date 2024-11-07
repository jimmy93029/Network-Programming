from utils.connection import connect_to_server
from .game1 import Tic_tac_toe
from .game2 import dark_chess


game_list = ["Tic_tac_toe", "dark_chess"]


"""Client A"""
def start_game1(client_socket, game_socket1, game_type):
    """
    房間創建者啟動遊戲伺服器，並處理遊戲邏輯。
    """
    print("Game starting as Room Host...")
    # 根據遊戲類型進行初始化
    client_socket.sendall(f"START_GAME {game_type}".encode())

    print("Waiting for Player B to connect...")
    PleyerA, _ = game_socket1.accept()
    print("Player B connected.")

    # 處理遊戲邏輯 (可根據不同遊戲類型添加具體實作)
    if game_type == game_list[0]:
        Tic_tac_toe(PleyerA, "A")
    else:
        Chinese_chess(PleyerA, "A")

    # 通知遊戲結束
    client_socket.sendall(b"FINISH")
    game_socket1.close()


"""Client B"""
def start_game2(client_socket, game_addr, game_type):
    """
    房間加入者連接到遊戲伺服器，參與遊戲。
    """
    try:
        print("Connecting to Game Server as Participant...")
        PlayerB = connect_to_server(game_addr)
        PlayerB.sendall(f"JOIN_GAME {game_type}".encode())

        # 處理遊戲邏輯 (可根據不同遊戲類型添加具體實作)
        if game_type == game_list[0]:
            Tic_tac_toe(PlayerB, "A")
        else:
            Chinese_chess(PlayerB, "A")

    except Exception as e:
        print(f"Error during game participation: {e}")
        retry(client_socket, game_addr, game_type)
    finally:
        PlayerB.close()

def retry(client_socket, game_addr, game_type):
    """
    提供房間加入者重新連接或退出選擇。
    """
    choose = input("Do you want to re-connect or exit the room? (reconnect/exit): ")
    if choose.lower() == "reconnect":
        start_game2(client_socket, game_addr, game_type)
    elif choose.lower() == "exit":
        client_socket.sendall("EXIT_ROOM".encode())
        print("Exited the room.")

def play_game_logic(game_socket, game_type):
    """
    處理遊戲的主要邏輯。這是遊戲運行期間的模擬，可以根據遊戲類型進行擴展。
    """
    print(f"Playing {game_type}...")
    while True:
        data = game_socket.recv(1024).decode()
        if data == "GAME_OVER":
            print("Game over.")
            break
        # 根據遊戲需求處理接收到的資料
        print(f"Received: {data}")
        game_socket.sendall(f"ACK: {data}".encode())

def handle_game_start(client, addr, rooms, online_users):
    """
    處理遊戲開始的伺服器端邏輯。
    """
    try:
        room_info = rooms.get(addr)
        if room_info:
            # 開始遊戲
            client.sendall("GAME_START".encode())
            print(f"Game started for room hosted by {addr}")
        else:
            client.sendall("ROOM_NOT_FOUND".encode())
    except Exception as e:
        print(f"Error during game start handling: {e}")
        client.sendall("GAME_START_FAILED".encode())

def handle_game_ending(client, addr, rooms, online_users):
    """
    處理遊戲結束的伺服器端邏輯。
    """
    try:
        room_info = rooms.pop(addr, None)
        if room_info:
            # 更新玩家狀態並通知遊戲結束
            host = room_info["creator"]
            online_users[host]["status"] = "idle"
            client.sendall("GAME_ENDED".encode())
            print(f"Game ended for room hosted by {host}")
        else:
            client.sendall("ROOM_NOT_FOUND".encode())
    except Exception as e:
        print(f"Error during game ending handling: {e}")
        client.sendall("GAME_END_FAILED".encode())
