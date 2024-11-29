from utils.connection import create_game_server
import time


"""Client B"""
def do_join_room(client_socket):
    # Choose a public room to join
    roomId = input("Which public room do you want to join: ")
    client_socket.sendall(f"JOIN1 {roomId}".encode())  # Encode the message to bytes

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
    joiner = message.split()[-1]

    # Create game server 
    game_socket1, ip_address, port = create_game_server()
    if ip_address is not None:
        client_socket.sendall(f"JOIN2 {ip_address},{port} {joiner}".encode())
        return "In Game mode1", game_socket1
    else:
        client_socket.sendall(f"JOIN2 STARTUP_FAILED {joiner}".encode())
        print("STARTUP_FAILED: Cannot create game server")
        return  # Early return if server creation failed
    
    # If successful, return game mode and game socket


"""Server"""
def handle_join1(data, client, addr, rooms, online_users, login_addr):
    _, roomId = data.split()

    # Check if room Id available
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
    joiner = login_addr[addr] 
    creator = rooms[roomId]["creator"]
    creator_socket = online_users[creator]["socket"]
    creator_socket.sendall(f"Request game IP, port from {joiner}".encode())


def handle_join2(data, client, addr, rooms, online_users, login_addr):
    _, message, joiner = data.split()

    creator = login_addr[addr]
    roomId = next((key for key, info in rooms.items() if info["creator"] == creator), None)
    joiner_socket = online_users[joiner]["socket"] 

    # Receive IP and port from the creator 
    if message == "STARTUP_FAILED":
        joiner_socket.sendall(b"STARTUP_FAILED: Please join another public room")
        return

    # Change status
    rooms[roomId]["status"] = "In Game"
    rooms[roomId]["participant"] = joiner
    online_users[creator]["status"] = "In Game"
    online_users[joiner]["status"] = "In Game"
    
    # Parse IP and port if provided correctly
    ip, port = message.split(',')
    game_type = rooms[roomId]["game_type"]
    joiner_socket.sendall(f"{ip} {port} {game_type}".encode())




