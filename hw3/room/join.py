from utils.connection import create_game_server
from utils.variables import IN_ROOM_PLAYER, IN_ROOM


"""Client B"""
def do_join_room(client_socket):
    """
    Sends a request to join a public room to the server and handles the response.
    """
    try:
        # Choose a public room to join
        room_name = input("Enter the name of the public room to join: ")
        client_socket.sendall(f"JOIN1 {room_name}".encode())  

        # Receive join confirmation
        message = client_socket.recv(1024).decode()
        if message == "Join request accepted":
            print("You have successfully joined the room.")
            return IN_ROOM_PLAYER
        else:
            print(f"Failed to join the room: {message}")
            return None

    except (ConnectionError, TimeoutError) as e:
        print(f"Failed to join the room due to network issue: {e}")
        return None


"""Server"""
def handle_join(data, client, addr, rooms, online_users, login_addr):
    """
    Handles a client's request to join a room.
    """
    try:
        _, room_name = data.split()

        # Check if the room exists
        if room_name not in rooms:
            client.sendall(b"Room does not exist")
            return

        room = rooms[room_name]

        # Check room status and type
        if room["status"] == "In Game":
            client.sendall(b"Room is currently in game")
            return
        elif room["room_type"] == "private":
            client.sendall(b"Cannot join a private room without an invitation")
            return
        elif len(room["participants"]) >= 1:  # Assuming max joiners is 1 (host + 1 player)
            client.sendall(b"Room is full")
            return

        # Add joiner to the room
        player = login_addr[addr]
        room["participants"].append(player)
        online_users[player]["status"] = IN_ROOM_PLAYER
        client.sendall(b"Join request accepted")

    except Exception as e:
        print(f"Error handling join request: {e}")
        client.sendall(b"Error: Unable to join the room.")


