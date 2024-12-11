import time
from utils.variables import IN_ROOM_PLAYER, STATUS, PLAYERS, ROOM_TYPE, IN_GAME, MAX_PLAYERS, PRIVATE, GAME
from game.download import update_game


"""Client B"""
def do_join_room(client_socket):
    """
    Sends a request to join a public room to the server and handles the response.
    """
    try:
        # Step1. Choose a public room to join
        room_name = input("Enter the name of the public room to join: ")
        client_socket.sendall(f"JOIN {room_name}".encode())  

        # Step2. Receive join confirmation
        message = client_socket.recv(1024).decode()
        if not message.startswith("Join request accepted"):
            print(f"Failed to join the room: {message}")
            return None
        
        print("You have successfully joined the room.")
        _, game_name = message.split(':')

        # Step3. Check and update game
        update_game(client_socket, game_name)
        
        return IN_ROOM_PLAYER

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

        # Step1. Check if the room exists or Check room status and type
        if room_name not in rooms:
            client.sendall(b"Room does not exist")
            return
        elif rooms[room_name][STATUS] == IN_GAME:
            client.sendall(b"Room is currently in game")
            return
        elif rooms[room_name][ROOM_TYPE] == PRIVATE:
            client.sendall(b"Cannot join a private room without an invitation")
            return
        elif len(rooms[room_name][PLAYERS]) >= MAX_PLAYERS:  # Assuming max joiners is 1 (host + 1 player)
            client.sendall(b"Room is full")
            return

        # Step2. Add joiner to the room
        player = login_addr[addr]
        rooms[room_name][PLAYERS].append(player)
        online_users[player][STATUS] = IN_ROOM_PLAYER
        client.sendall(f"Join request accepted:{rooms[room_name][GAME]}".encode())

    except Exception as e:
        print(f"Error handling join request: {e}")
        client.sendall(b"Error: Unable to join the room.")


