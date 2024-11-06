from ..game import game_list


room_list = ["private", "public"]

""" Client """
def do_create_room(client_socket, retry=0):

    try:
        game_type = selects_type(choice_name="game type", choice_list=game_list)
        room_type = selects_type(choice_name="room type", choice_list=room_list)
    
        message = f"CREATE {game_list[game_type-1]} {room_list[room_type-1]}"
        client_socket.sendall(message.encode())

        response = client_socket.recv(1024).decode()
        print(response)

        if response == "Create rooom successfully":
            return "In Room"
        elif not retry:
            return do_create_room(client_socket, retry=1)
        
    except (ConnectionError, TimeoutError) as e:
        print(f"Create Room failed due to network issue: {e}")
        if not retry:
            return do_create_room(client_socket, retry=1)


def selects_type(choice_name, choice_list, choice="0"): 

    while not choice.isdigit() or int(choice) not in [1, 2]:
        choice = input(f"Which {choice_name} do you want? \n\
                        (1) {choice_list[0]} \n\
                        (2) {choice_list[1]} \n")

        if not choice.isdigit():
            print(f"Please input {choice_name} as a digit.")
        elif int(choice) not in [1, 2]:
            print(f"Please input {choice_name} as a number from {{1, 2}}.")

    return int(choice)


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
        rooms[room_id] = room_info
        online_users[username] = "In room"
        
    except Exception as e:
        print(f"Server encountered an error during creating room: {e}")
        client.sendall("Create room failed: Server error.".encode())

