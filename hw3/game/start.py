from utils.connection import connect_to_server
from utils.tools import select_type
from .game1 import Tic_tac_toe
from .game2 import dark_chess
import time

game_list = ["Tic_tac_toe", "dark_chess"]

""" Client A """
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
    message = client_socket.recv(1024).decode()  # Wait for a message from the lobby server
    print(message)
    if message == "PlayerB exit":
        return "idle"  # If Player B exits, return "idle" to reset state

    # Accept connection from Player B
    PlayerA, _ = game_socket1.accept()
    print("Player B connected.")

    # Start the appropriate game session based on the selected game type
    if game_type == game_list[0]:
        broke = Tic_tac_toe(PlayerA, "A")
    else:
        broke = dark_chess(PlayerA, "A")

    # Notify the lobby server that the game has ended
    if not broke:
        client_socket.sendall(b"FINISH")
        time.sleep(4)
    PlayerA.close()  # Close Player A’s socket after game completion
    game_socket1.close()  # Close the game server socket

    return "idle"


""" Client B """
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
        PlayerB = connect_to_server(game_addr)  # Connect to game server
        client_socket.sendall(b"START successfully")

    except Exception as e:
        print(f"Error during game participation: {e}")
        retry(client_socket, game_addr, game_type)
        return "idle"  # Return "idle" if an error occurs

    # Start the appropriate game session based on the selected game type
    if game_type == game_list[0]:
        Tic_tac_toe(PlayerB, "B")
    else:
        dark_chess(PlayerB, "B")

    PlayerB.close()  # Close Player B’s socket after game completion

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
        start_game2(client_socket, game_addr, game_type)  # Retry connecting
    else:
        client_socket.sendall(b"START failed")  # Send failure message to lobby server
        print("Exited the room.")


"""Server"""
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
    playerb = rooms[roomId].get("participant")

    # Update room and player statuses, handling if playerb is already disconnected
    rooms.pop(roomId, None)
    online_users[playera]["status"] = "idle"
    
    if playerb in online_users:
        online_users[playerb]["status"] = "idle"
    else:
        print(f"{playerb} is already disconnected or not in the game.")

    print(f"Room {roomId} closed. Both players set to idle.")

