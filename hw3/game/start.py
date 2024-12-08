import time
from utils.connection import connect_to_server, create_game_server
from utils.tools import select_type
from utils.variables import IDLE, IN_ROOM_HOST, IN_ROOM_PLAYER
from .games import Tic_tac_toe, dark_chess


""" Client A: Host """
def start_game1(client_socket, game_type):
    """
    Host starts the game server and manages game logic.
    """
    # Step 1: Host requests the server to check if the room is full
    client_socket.sendall(b"START_REQUEST")
    server_response = client_socket.recv(1024).decode()

    if server_response == "NO":
        print("Cannot start the game. Room is not full.")
        return IN_ROOM_HOST

    # Step 2: Create the game server
    game_socket, ip_address, port = create_game_server()
    if not game_socket:
        print("Failed to start the game server.")
        return IN_ROOM_HOST

    # Step 3: Send game server details to the server
    game_server_info = f"START_GAME {ip_address} {port}"
    client_socket.sendall(game_server_info.encode())

    # Step 4: Wait for confirmation from the server
    participants_status = client_socket.recv(1024).decode()
    if participants_status != "SUCCESS":
        print("One or more participants failed to connect.")
        game_socket.close()
        return IN_ROOM_HOST

    print("All participants connected successfully. Starting the game...")

    # Step 5: Accept connection from the participant
    participant, _ = game_socket.accept()
    print("Participant connected.")

    # Step 6: Start the selected game
    if game_type == "Tic Tac Toe":
        Tic_tac_toe(participant, "A")
    else:
        dark_chess(participant, "A")

    # Step 7: Notify the server that the game has ended
    client_socket.sendall(b"FINISH")
    time.sleep(2)
    game_socket.close()

    return IDLE


""" Client B: Participant """
def start_game2(client_socket, game_addr, game_type):
    """
    Participant connects to the game server and joins the game.
    """
    try:
        # Step 1: Connect to the game server
        print("Connecting to the game server...")
        participant_socket = connect_to_server(game_addr)
        client_socket.sendall(b"CONNECT SUCCESS")
    except Exception as e:
        print(f"Error connecting to game server: {e}")
        client_socket.sendall(b"CONNECT FAIL")
        return IN_ROOM_PLAYER

    # Step 2: Start the selected game
    if game_type == "Tic Tac Toe":
        Tic_tac_toe(participant_socket, "B")
    else:
        dark_chess(participant_socket, "B")

    participant_socket.close()
    return IDLE


""" Server """
def handle_game_start_request(data, client, addr, rooms, login_addr, online_users):
    """
    Handles a game start request from the host.
    """
    # Step 1: Check if the room is full
    host = login_addr[addr]
    room_name = next((key for key, info in rooms.items() if info["creator"] == host), None)
    room = rooms[room_name]

    if not room or len(room.get("participants", [])) < 1:  # 1 participant is required
        client.sendall(b"NO")
        return

    # Step 2: Notify the host that the room is full
    client.sendall(b"YES")

    # Step 3: Notify all participants to prepare for the game
    participants = room["participants"]
    for participant in participants:
        participant_socket = online_users[participant]["socket"]
        participant_socket.sendall(b"GAME_START")


def handle_game_server_details(data, client, addr, rooms, online_users):
    """
    Receives game server details from the host and sends them to the participant.
    """
    # Step 1: Parse game server details
    _, room_id, ip_address, port = data.split()
    room = rooms.get(room_id)

    if not room:
        return

    # Step 2: Send game server details to the participant
    participant = room["participants"][0]  # Assuming one participant
    participant_socket = online_users[participant]["socket"]
    game_info = f"GAME_INFO {ip_address} {port}"
    participant_socket.sendall(game_info.encode())

    # Step 3: Wait for the participant's connection status
    response = participant_socket.recv(1024).decode()
    if response == "CONNECT SUCCESS":
        # Step 4: Notify the host and update statuses
        client.sendall(b"SUCCESS")
        online_users[room["creator"]]["status"] = "In Game"
        online_users[participant]["status"] = "In Game"
        room["status"] = "In Game"
    else:
        client.sendall(b"FAIL")


def handle_game_ending(data, client, addr, rooms, online_users):
    """
    Handles the end of the game, updating room and player statuses.
    """
    # Step 1: Identify the room and players
    _, room_id = data.split()
    room = rooms.pop(room_id, None)

    if room:
        players = [room["creator"]] + room.get("participants", [])
        # Step 2: Update all players' statuses to idle
        for player in players:
            if player in online_users:
                online_users[player]["status"] = "idle"

    print(f"Room {room_id} closed and all players set to idle.")

