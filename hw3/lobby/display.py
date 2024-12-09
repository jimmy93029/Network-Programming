from utils.tools import format_table
from utils.variables import NAME, HOST, STATUS, ROOM_TYPE, GAME, MESSAGE, IDLE, ADDRESS


""" Client """
def do_listing_online_players(client_socket):
    """
    Lists all online players.
    """
    try:
        client_socket.sendall(b"DISPLAY ONLINE")
        response = client_socket.recv(1024).decode()
        print(response)
    except (ConnectionError, TimeoutError) as e:
        print(f"Display failed due to network issue: {e}")


def do_listing_rooms(client_socket):
    """
    Lists all public rooms.
    """
    try:
        client_socket.sendall(b"DISPLAY ROOM")
        response = client_socket.recv(1024).decode()
        print(response)
    except (ConnectionError, TimeoutError) as e:
        print(f"Display failed due to network issue: {e}")


def do_listing_available_players(client_socket):
    """
    Lists all idle (available) players.
    """
    try:
        client_socket.sendall(b"DISPLAY AVAILABLE")
        response = client_socket.recv(1024).decode()
        print(response)
    except (ConnectionError, TimeoutError) as e:
        print(f"Display failed due to network issue: {e}")


def do_listing_invitations(client_socket):
    """
    Lists all invitations sent to the client.
    """
    try:
        client_socket.sendall(b"DISPLAY INVITATIONS")
        response = client_socket.recv(4096).decode()
        print(response)
    except (ConnectionError, TimeoutError) as e:
        print(f"Display failed due to network issue: {e}")


""" Server """
def handle_display(data, client, addr, login_addr, online_users, rooms, invitations):
    """
    Handle display requests from the client.
    """
    _, option = data.split()
    if option == "ONLINE":
        message = show_players(online_users, available=False)  # Show all players
    elif option == "AVAILABLE":
        message = show_players(online_users, available=True)  # Show idle players only
    elif option == "ROOM":
        message = show_rooms(rooms)
    elif option == "INVITATIONS":
        invitee = login_addr[addr]
        message = show_invitations(invitations, invitee)
    else:
        message = "Invalid display option."
    client.sendall(message.encode())


def show_players(online_users, available=False):
    """
    Format and return a table of players.
    """
    if available:
        # Filter idle players
        filtered_users = {username: info for username, info in online_users.items() if info[STATUS] == IDLE}
        title = "Available Players"
    else:
        # Show all players
        filtered_users = online_users
        title = "Online Players"

    # Define table structure (headers remain the same)
    header = ["Address", "Player", "Status"]
    rows = [[str(info[ADDRESS]), username, info[STATUS]] for username, info in filtered_users.items()]
    column_widths = [30, 10, 10]

    # Format table (even if rows are empty)
    table = format_table(header, rows, column_widths, title=title, count=len(rows))
    return table


def show_rooms(rooms):
    """
    Format and return the public rooms in a table format as a string.
    """
    header = [NAME, HOST, STATUS, ROOM_TYPE, GAME]
    rows = [[room_id, info[HOST], info[STATUS], info[ROOM_TYPE], info[GAME]]
            for room_id, info in rooms.items()]
    column_widths = [15, 10, 10, 12, 10]

    # Format table (even if rows are empty)
    table = format_table(header, rows, column_widths, title="Room Table", count=len(rows))
    return table


def show_invitations(invitations, invitee):
    """
    Format and return all invitations received by the invitee in a table format.
    """
    header = ["invitor", "room", "room status", "message"]
    rows = [
        [invitor, info[NAME], info[STATUS], info[MESSAGE]]
        for invitor, info in invitations.get(invitee, {}).items()
    ]
    column_widths = [10, 15, 20, 30]
    table = format_table(header, rows, column_widths, title="Invitations Table", count=len(rows))
    return table


