from utils.tools import select_type
from utils.variables import IN_ROOM_HOST, Room_list, HOST, STATUS, ROOM_TYPE, GAME, PLAYERS, WAITING


""" Client """
def do_create_room(client_socket):
    """
    Sends a request to create a room to the server and handles the response.
    """
    try:
        # Collect room details from the user
        room_name = input("Enter Room Name: ")
        room_idx = select_type(choice_name="Room type", choice_list=Room_list)
        game_type = input("Enter the game you want to play: ")

        # Send the room creation request to the server
        message = f"CREATE {room_name} {game_type} {Room_list[room_idx - 1]}"
        client_socket.sendall(message.encode())

        # Receive and handle the server's response
        response = client_socket.recv(1024).decode()
        print(response)

        if response == "Create room successfully":
            return IN_ROOM_HOST

    except (ConnectionError, TimeoutError) as e:
        print(f"Create Room failed due to network issue: {e}")

    return None


""" Server """
def handle_create_room(data, client, addr, rooms, login_addr, online_users, game_list):
    """
    Handles the room creation request from the client.
    """
    try:
        # Parse the client's room creation request
        _, room_name, game_type, room_type = data.split()

        # Check if the game type exists in the server's game list
        if game_type not in game_list:
            client.sendall(b"Error: Selected game type does not exist.")
            return

        # Check for duplicate room names
        if room_name in rooms:
            client.sendall(b"Error: Room name already exists.")
            return

        # Add the room to the server's room list
        username = login_addr[addr]
        room_info = {
            HOST: username,
            GAME: game_type,
            ROOM_TYPE: room_type,
            STATUS: WAITING,
            PLAYERS: []
        }

        rooms[room_name] = room_info
        online_users[username][STATUS] = IN_ROOM_HOST
        client.sendall(b"Create room successfully")

    except Exception as e:
        print(f"Server encountered an error during room creation: {e}")
        client.sendall(b"Error: Server encountered an issue while creating the room.")


