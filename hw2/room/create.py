from game.start import game_list
from utils.tools import select_type

room_list = ["private", "public"]

""" Client """
def do_create_room(client_socket, retry=0):

    try:
        game_idx = selects_type(choice_name="game type", choice_list=game_list)
        room_idx = selects_type(choice_name="room type", choice_list=room_list)
    
        message = f"CREATE {game_list[game_idx-1]} {room_list[room_idx-1]}"
        client_socket.sendall(message.encode())

        response = client_socket.recv(1024).decode()
        print(response)

        if response == "Create rooom successfully":
            return f"In Room {room_list[room_idx-1]}", game_list[game_idx-1]
        elif not retry:
            return do_create_room(client_socket, retry=1)
        
    except (ConnectionError, TimeoutError) as e:
        print(f"Create Room failed due to network issue: {e}")
        if not retry:
            return do_create_room(client_socket, retry=1)


""" Server """
def handle_create_room(data, client, addr, rooms, login_addr, online_users):
    try:
        _, game_type, room_type = data.split() 
        room_id = len(rooms) + 1  

        username = login_addr[addr]
        room_info = {
            "creator": username,
            "game_type": game_type,
            "room_type": room_type,
            "status": "Waiting"
        }

        client.sendall(b"Create rooom successfully")
        rooms[f"{room_id}"] = room_info
        online_users[username]["status"] = "In Room"
        
    except Exception as e:
        print(f"Server encountered an error during creating room: {e}")
        client.sendall("Create room failed: Server error.".encode())

