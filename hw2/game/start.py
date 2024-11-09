from utils.connection import connect_to_server
from utils.tools import select_type
from .game1 import Tic_tac_toe
from .game2 import dark_chess

game_list = ["Tic_tac_toe", "dark_chess"]


"""Client A"""
def start_game1(client_socket, game_socket1, game_type):
    """
    The room creator starts the game server and manages game logic.
    Preconditions:
        - The room has been created successfully.
        - The game type has been selected during room creation.
    Trigger:
        - Game starts automatically when two players are in the room.
    """
    print("Waiting for Player B to connect...")
    message = client_socket.recv(1024).decode()
    print(message)
    if message == "PlayerB exit":
        return

    # Accept the connection from Player B
    PlayerA, _ = game_socket1.accept()
    print("Player B connected.")

    # Start the game session based on the selected game type
    if game_type == game_list[0]:
        Tic_tac_toe(PlayerA, "A")
    else:
        dark_chess(PlayerA, "A")

    # Notify the lobby server that the game has ended
    client_socket.sendall(b"FINISH")
    game_socket1.close()

    return "idle"


"""Client B"""
def start_game2(client_socket, game_addr, game_type):
    """
    The room joiner connects to the game server and participates in the game.
    Preconditions:
        - The room joiner has successfully joined the room.
        - The room creator has started the game server.
    """
    # Attempt to connect to the game server as Player B
    try:
        print("Connecting to Game Server as Participant...")
        PlayerB = connect_to_server(game_addr)
        client_socket.sendall("START successfully".encode())

    except Exception as e:
        print(f"Error during game participation: {e}")
        retry(client_socket, game_addr, game_type)
        return
 
    # Start the game session based on the selected game type
    if game_type == game_list[0]:
        Tic_tac_toe(PlayerB, "B")
    else:
        dark_chess(PlayerB, "B")

    # Close Player B's connection after the game ends
    PlayerB.close()

    return "idle"


def retry(client_socket, game_addr, game_type):
    """
    Offers the room joiner the option to reconnect or exit the room.
    Extension:
        - If the room joiner is unable to connect to the game server, they can retry or exit.
    """
    options = ["reconnect", "exit"]
    idx = select_type("options", options)

    if options[idx-1] == "reconnect":
        start_game2(client_socket, game_addr, game_type)
    else:
        client_socket.sendall("START_GAME failed".encode())
        print("Exited the room.")


def handle_game_start(data, client, addr, rooms, login_addr, online_users):
    """
    Handles game start signaling between the lobby server and game server.
    Main Success Scenario:
        - The room joiner connects to the room creator's game server via the lobby server.
        - Both players start the game.
    """
    _, message = data.split()

    playerb = login_addr[addr]
    roomId = next((key for key, info in rooms.items() if info["participant"] == playerb), None)
    creator = rooms[roomId]["creator"]
    playera_socket = online_users[creator]["socket"]

    # Notify room creator if Player B connected or exited
    if message == "successfully":
        playera_socket.send(b"PlayerB connect successfully")
    else:
        playera_socket.send(b"PlayerB exit")


def handle_game_ending(data, client, addr, rooms, login_addr, online_users):
    """
    Handles game ending and updates room and player statuses.
    Postconditions:
        - The game room is dissolved.
        - Both players' statuses are updated to "idle" in the lobby server.
    """
    playera = login_addr[addr]
    roomId = next((key for key, info in rooms.items() if info["creator"] == playera), None)
    playerb = rooms[roomId]["participant"]
    
    # Update statuses to idle and remove room from public list
    rooms.pop(roomId, None)
    online_users[playera]["status"] = "idle"
    online_users[playerb]["status"] = "idle"
