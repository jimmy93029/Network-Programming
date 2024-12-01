from utils.tools import format_table


""" Client """
def do_showing_players(client_socket):
    try:
        client_socket.sendall(b"DISPLAY ONLINE")
        response = client_socket.recv(1024).decode()
        print(response)
    
    except (ConnectionError, TimeoutError) as e:
        print(f"Display failed due to network issue: {e}")


def do_showing_rooms(client_socket):
    try:
        client_socket.sendall(b"DISPLAY ROOM")
        response = client_socket.recv(1024).decode()
        print(response)
    
    except (ConnectionError, TimeoutError) as e:
        print(f"Display failed due to network issue: {e}")

    
""" Server """
def handle_display(data, client, addr, online_users, rooms):
    _, option = data
    if option == "ONLINE":
        message = show_players(online_users)
    else:
        message = show_rooms(rooms) 
    client.sendall(message.encode())


def show_players(online_users):
    """
    Format and return the online players in a table format as a string.
    """
    if online_users:
        header = ["Address", "Player", "Status"]
        rows = [[str(info["address"]), username, info["status"]]
                for username, info in online_users.items()]
        column_widths = [30, 10, 10]  # Adjust column widths to match the format in the image
        table = format_table(header, rows, column_widths, title="Player List", count=len(online_users))
        return table
    else:
        return "Currently, no players are online."


def show_rooms(rooms):
    """
    Format and return the public rooms in a table format as a string.
    """
    public_rooms = [info for room_id, info in rooms.items() if info["room_type"] == "public"]

    if public_rooms:
        header = ["Name", "Host", "Status", "Room Type", "Game"]
        rows = [[room_id, info["creator"], info["status"], info["room_type"], info["game_type"]]
                for room_id, info in rooms.items() if info["room_type"] == "public"]
        column_widths = [15, 10, 10, 12, 10]  # Adjust column widths as needed
        table = format_table(header, rows, column_widths, title="Room Table", count=len(public_rooms))
        return table
    else:
        return "No public rooms waiting for players."

