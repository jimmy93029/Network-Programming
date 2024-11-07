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
    print(message)
    if message.startswith("STARTUP_FAILED"):
        return None, None
    
    # Split IP and port and handle as a tuple
    ip, port = message.split()
    game_addr = (ip, int(port))

    return "In Game mode2", game_addr


"""Client A"""
def wait_for_join(client_socket):
    # Receive invitation from Client B
    print("Waiting for client B to join...")
    message = client_socket.recv(1024).decode()  
    print(message)

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
    if rooms[roomId]["status"] == "In game":
        client.sendall(b"Room is full")
    elif rooms[roomId]["room_type"] == "private":
        client.sendall(b"Cannot join private room")
    else:
        client.sendall(b"Join request accept")

    # Request Game Ip, port
    creator = rooms[roomId]["creator"]
    creator_socket = online_users[creator]["socket"]
    creator_socket.sendall(b"Request game Ip, port")
    message = creator_socket.resv(1024).encode()

    if message == "STARTUP_FAILED":
        client.sendall("STARTUP_FAILED : Please join another public room")
        return
    else:
        ip, port = message
        client.sendall(f"{ip} {port}".encode())

    # Change status
    joiner = login_addr[addr]
    rooms[roomId]["status"] = "In Game"
    online_users[creator]["status"] = "In Game"
    online_users[joiner]["status"] = "In Game"


def catch_server_error():
    pass


