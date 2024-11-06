from ..connection import connect_to_server


""" Client """
def do_display():
    try:
        client_socket = connect_to_server()
        client_socket.sendall(b"LOGOUT")
        
        response = client_socket.recv(1024).decode()
        print(response)

        client_socket.close()
    
    except (ConnectionError, TimeoutError) as e:
        print(f"Display failed due to network issue: {e}")

    
""" Server """
def handle_display(client, online_users, rooms):
    message = show_online(online_users) + "\n" + show_rooms(rooms) + "\n"
    client.sendall(message.encode())


# The names and statuses of all currently online players (e.g., playing, idle).
def show_online(online_users):
    if online_users:
        online_list = "\t".join([f"{username}: {info['status']}" for username, info in online_users.items()])
        return f"Online players: {online_list}"
    else:
        return "Currently, no players are online."


# All public game rooms (including the creator, game type, and room status).
def show_rooms(rooms):
    if rooms:
        room_list = "\t".join([f"RoomId = {room_id}: Creator={info['creator']}, GameType={info['game_type']}, Status={info['status']}" 
                               for room_id, info in rooms.items() if info['status'] == "public"])
        return f"Available rooms: {room_list}"
    else:
        return "No public rooms waiting for players."

