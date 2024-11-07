from utils.connection import create_game_server


"""Client B"""
def do_join_room(client_socket):
    # Choose a public room to join
    roomId = input("Which public room do you want to join: ")
    client_socket.sendall(f"JOIN {roomId}".encode())  # Encode the message to bytes

    # Receive join confirmation
    message = client_socket.recv(1024).decode()
    if message != "Join request accept":
        print(message)
        return None, None

    # Acquire IP and port
    message = client_socket.recv(1024).decode()  # Receive the IP and port message
    print(f"Server response : {message}")
    if message.startswith("STARTUP_FAILED"):
        return None, None
    else:
        # Split IP and port and handle as a tuple
        ip, port, game_type = message.split()
        game_addr = (ip, int(port))

    return "In Game mode2", game_addr, game_type


"""Client A"""
def wait_for_join(client_socket):
    # Receive invitation from Client B
    print("Waiting for client B to join...")
    message = client_socket.recv(1024).decode()  
    print(f"Server response : {message}")

    # Create game server 
    game_socket1, ip_address, port = create_game_server()
    if ip_address is not None:
        client_socket.sendall(f"{ip_address} {port}".encode())
    else:
        client_socket.sendall(b"STARTUP_FAILED")
        print("STARTUP_FAILED: Cannot create game server")
        return  # Early return if server creation failed
    
    # If successful, return game mode and game socket
    return "In Game mode1", game_socket1
 

"""Server"""
def handle_join(data, client, addr, rooms, online_users, login_addr):
    # Check if room Id available
    _, roomId = data.split()
    if roomId not in rooms:
        client.sendall(b"Room does not exist")
        return
    
    if rooms[roomId]["status"] == "In Game":
        client.sendall(b"Room is full")
        return
    elif rooms[roomId]["room_type"] == "private":
        client.sendall(b"Cannot join private room")
        return
    else:
        client.sendall(b"Join request accept")

    # Request Game IP, port
    creator = rooms[roomId]["creator"]
    creator_socket = online_users[creator]["socket"]
    creator_socket.sendall(b"Request game IP, port")

    # Receive IP and port from the creator
    message = creator_socket.recv(1024).decode()  # Corrected `recv` and added `decode`
    
    if message == "STARTUP_FAILED":
        client.sendall(b"STARTUP_FAILED: Please join another public room")
        return
    else:
        # Parse IP and port if provided correctly
        ip, port = message.split()
        game_type = rooms[roomId]["game_type"]
        client.sendall(f"{ip} {port} {game_type}".encode())

    # Change status
    joiner = login_addr[addr]
    rooms[roomId]["status"] = "In Game"
    online_users[creator]["status"] = "In Game"
    online_users[joiner]["status"] = "In Game"


