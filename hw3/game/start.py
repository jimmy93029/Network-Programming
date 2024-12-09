import time
from utils.connection import connect_to_server, create_game_server
from utils.variables import IDLE, IN_ROOM_HOST, IN_ROOM_PLAYER
import subprocess


""" Client A: Host """
def do_starting_game1(client_socket):
    """
    Host starts the game server and manages game logic.
    """
    # Step 1: Request game start from the server
    game_type = request_game_start(client_socket)
    if game_type is None:
        return IN_ROOM_HOST

    # Step 2: Create game server
    game_socket = connecting_game(client_socket)
    if game_socket is None:
        return IN_ROOM_HOST

    # Step 3: Wait for participant to connect
    game_connection, _ = game_socket.accept()
    print("Participant connected.")

    # Step 4: Run the game
    in_game(game_type, game_connection, "A")

    # Step 5: Notify server of game completion
    client_socket.sendall(b"GAME ENDING 0")

    return IDLE


def request_game_start(client_socket):
    """
    Sends a request to the server to check if the room is ready to start the game.
    """
    client_socket.sendall(b"GAME REQUEST 0")
    server_response = client_socket.recv(1024).decode()

    if server_response.startswith("NO"):
        print("Cannot start the game. Room is not full.")
        return None
    else:
        _, game_type = server_response.split()
        return game_type


def connecting_game(client_socket):
    """
    Creates a game server and sends its details to the main server.
    """
    game_socket, ip_address, port = create_game_server()
    if not game_socket:
        print("Failed to start the game server.")
        return None

    # Send server details to the main server
    game_server_info = f"GAME SERVER {ip_address}|{port}"
    client_socket.sendall(game_server_info.encode())

    # Wait for server confirmation
    participants_status = client_socket.recv(1024).decode()
    if participants_status != "SUCCESS":
        print("Participant failed to connect. Closing server.")
        game_socket.close()
        return None

    print("Participant connected successfully. Starting the game...")
    return game_socket


def in_game(game_type, game_socket, role):
    """
    Executes the selected game type.
    """
    subprocess.run(["python", f"{game_type}.py", role, str(game_socket.fileno())])

    # Close the game socket after completion
    game_socket.close()


""" Client B: Participant """
def do_starting_game2(client_socket):
    """
    Participant connects to the game server and joins the game.
    """
    try:
        # Receive game server details from the main server
        game_info = client_socket.recv(1024).decode()
        game_type, ip_address, port = game_info.split()

        # Connect to the game server
        game_socket = connect_to_server((ip_address, int(port)))
        client_socket.sendall(b"CONNECT SUCCESS")

    except Exception as e:
        print(f"Error connecting to game server: {e}")
        client_socket.sendall(b"CONNECT FAIL")
        return IN_ROOM_PLAYER

    # Join and play the game
    in_game(game_type, game_socket, "B")
    return IDLE


""" Server """
def handle_game_issue(data, client, addr, rooms, login_addr, online_users):
    _, option, info = data.split()
    host = login_addr[addr]
    room_name = next((key for key, info in rooms.items() if info["creator"] == host), None)
    room = rooms[room_name]

    if option == "REQUEST":
        game_start_request(client, room, online_users)
    elif option == "SERVER":
        ip_address, port = info.split('|')
        game_server_details(client, room, ip_address, port, online_users)
    elif option == "ENDING":
        game_ending(room_name, rooms, online_users)


def game_start_request(client, room, online_users):
    """
    Handles a game start request from the host.
    """
    # Step 1: Check if the room is full
    if not room or len(room.get("participants", [])) < 1:  # 1 participant is required
        client.sendall(b"NO")
        return

    # Step 2: Notify the host that the room is full
    client.sendall(f"YES {room['game_type']}".encode())

    # Step 3: Notify all participants to prepare for the game
    participants = room["participants"]
    for participant in participants:
        participant_socket = online_users[participant]["socket"]
        participant_socket.sendall(b"GAME_START")


def game_server_details(server_to_host, room, ip_address, port, online_users):
    """
    Receives game server details from the host and sends them to the participant.
    """
    # Step 2: Send game server details to the participant
    time.sleep(3)
    participant = room["participants"][0]  # Assuming one participant
    participant_socket = online_users[participant]["socket"]
    game_info = f"{room['game type']} {ip_address} {port}"
    participant_socket.sendall(game_info.encode())

    # Step 3: Wait for the participant's connection status
    response = participant_socket.recv(1024).decode()
    if response == "CONNECT SUCCESS":
        # Step 4: Notify the host and update statuses
        server_to_host.sendall(b"SUCCESS")
        online_users[room["creator"]]["status"] = "In Game"
        online_users[participant]["status"] = "In Game"
        room["status"] = "In Game"
    else:
        server_to_host.sendall(b"FAIL")


def game_ending(room_name, rooms, online_users):
    """
    Handles the end of the game, updating room and player statuses.
    """
    # Step 1: Identify the room and players
    room = rooms.pop(room_name, None)
    players = [room["creator"]] + room.get("participants", [])

    # Step 2: Update all players' statuses to idle
    for player in players:
        if player in online_users:
            online_users[player]["status"] = "idle"

    print(f"Room {room_name} closed and all players set to idle.")

