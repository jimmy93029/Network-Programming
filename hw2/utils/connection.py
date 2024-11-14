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
    while True:
        try:
            # Create a socket and bind to an available port
            game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            game_socket.bind(('', 0))  # Bind to all interfaces and let the OS choose a port
            game_socket.listen(5)

            # Get the chosen por
            port = game_socket.getsockname()[1]

            # Get the actual IP address of the server
            ip_address = socket.gethostbyname(socket.gethostname())
            print(f"Game server is running on IP: {ip_address}, Port: {port}")

            return game_socket, ip_address, port  # Return server information on success

        except OSError as e:
            # Catch port already in use or other binding errors
            print(f"Error starting game server: {e}")
            retry = input("Game server failed to start. Do you want to retry with a different port? (yes/no): ")
            if retry.lower() != 'yes':
                print("Game server setup aborted.")
                return None, None, None  # Return None values on failure
            

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
