

""" Client """
def do_display(client_socket):
    try:
        client_socket.sendall(b"DISPLAY")
        response = client_socket.recv(1024).decode()
        print(response)
    
    except (ConnectionError, TimeoutError) as e:
        print(f"Display failed due to network issue: {e}")

    
""" Server """
def handle_display(data, client, addr, online_users, rooms):
    message = show_online(online_users) + "\n" + show_rooms(rooms) + "\n"
    client.sendall(message.encode())


# The names and statuses of all currently online players (e.g., playing, idle).
def show_online(online_users):
    if online_users:
        online_list = " | ".join([f"{username}: {info['status']}" for username, info in online_users.items()])
        return f"Online players: {online_list}"
    else:
        return "Currently, no players are online."


# All public game rooms (including the creator, game type, and room status).
def show_rooms(rooms):
    print(f"rooms = {rooms}")
    if rooms:
        room_list = " | ".join([f"RoomId = {room_id}: Creator={info['creator']}, GameType={info['game_type']}, Status={info['status']}" 
                               for room_id, info in rooms.items() if info['room_type'] == "public"])
        return f"Available rooms: {room_list}"
    else:
        return "No public rooms waiting for players."

