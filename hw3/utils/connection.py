import socket

HOST = '127.0.0.1'  # Server IP
PORT = 10005        # Port 


def bind_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
    return server_socket


def connect_to_server(addr=(HOST, PORT)):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(addr)
    return client_socket


def create_game_server():
    """
    Creates a game server socket and binds it to an available port.
    """
    while True:
        try:
            # Step 1: Create a socket and bind to an available port
            game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            game_socket.bind(("", 0))  # Bind to all interfaces and use an OS-selected port
            game_socket.listen(5)

            # Step 2: Retrieve the IP address and port
            ip_address = socket.gethostbyname(socket.gethostname())
            port = game_socket.getsockname()[1]
            print(f"Game server running on {ip_address}:{port}")
            return game_socket, ip_address, port
        except OSError as e:
            # Step 3: Handle port binding errors
            print(f"Error creating game server: {e}")
            retry = input("Retry creating game server? (yes/no): ")
            if retry.lower() != "yes":
                return None, None, None
            

def handle_disconnected(client, addr, online_users, login_addr, rooms):
    username = login_addr.get(addr)
    
    print(f"Handling disconnection for {username}")

    # Check if the user was in a game
    for room_id, room_info in rooms.items():
        if room_info["creator"] == username or room_info.get("participant") == username:
            # Update the other player’s status
            other_player = (
                room_info["creator"] if room_info["creator"] != username else room_info.get("participant")
            )
            if other_player:
                online_users[other_player]["status"] = "idle"
            
            # Remove the room and set both players to idle
            online_users[username]["status"] = "idle"
            rooms.pop(room_id, None)
            print(f"Room {room_id} closed due to disconnection of {username}")
            break

    # Remove user from online_users and login_addr
    online_users.pop(username, None)
