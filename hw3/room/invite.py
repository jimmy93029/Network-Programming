from utils.variables import IN_ROOM_PLAYER, IN_ROOM, NAME, STATUS, MESSAGE, PLAYERS, HOST, IDLE, MAX_PLAYERS, GAME
from utils.tools import input_without
from game.download import check_and_update_game, check_and_sending_game


"""Client A"""
def do_invite(client_socket):
    invitee = input("Which idle user do you want to choose: ")
    message = input_without('|', "What is your invitation message")
    client_socket.sendall(f"INVITE|SEND|{invitee}|{message}".encode())

    response = client_socket.recv(1024).decode()
    if response.startswith("Invite failed"):
        print(response)
    else:
        print("Invitation sent successfully!")


"""Client B"""
def do_reply_invitation(client_socket):
    """
    Handles replying to an invitation from an invitor.
    """
    invitor = input("Enter the name of the invitor to reply to: ")
    client_socket.sendall(f"INVITE|REPLY|{invitor}".encode())

    response = client_socket.recv(1024).decode()
    if response.startswith("Reply error") or response.startswith("Reply failed"):
        print(response)
        return
    elif response.startswith("Success"):
        _, game_type = response.split(" ")
        print(f"Invitation accepted! Game type: {game_type}")
    else:
        print("Unexpected response from server.")
        return

    # Send the current game version to the server
    check_and_update_game(client_socket, game_type)
    print("You are now IN_ROOM_PLAYER.")
    return IN_ROOM_PLAYER


"""Server"""
def handle_invite(data, server_to_client, addr, login_addr, online_users, invitations, rooms):
    """
    Handles all invitation-related operations.
    """
    _, option, info = data.split('|', maxsplit=2)

    if option == "SEND":
        invitor = login_addr[addr]
        invitee, message = info.split("|", maxsplit=1)
        handle_send_invite(server_to_client, invitor, invitee, message, online_users, invitations, rooms)
    elif option == "REPLY":
        invitor = info
        invitee = login_addr[addr]
        handle_reply_invite(server_to_client, invitor, invitee, online_users, invitations, rooms)


def handle_send_invite(server_to_inviter, invitor, invitee, message, online_users, invitations, rooms):
    """
    Handles sending an invitation from the inviter to the invitee.
    """
    try:
        room_name = next(key for key, info in rooms.items() if info[HOST] == invitor)

        if invitee not in online_users:
            server_to_inviter.sendall(b"Invite failed: Invitee is not connected")
            return
        elif len(rooms[room_name][PLAYERS]) >= MAX_PLAYERS:
            server_to_inviter.sendall(b"Invite failed: Room is already full")
            return
        elif online_users[invitee][STATUS] != IDLE:
            server_to_inviter.sendall(b"Invite failed: User is not idle")
            return
        else:
            server_to_inviter.sendall(b"Success")

        invitations.setdefault(invitee, {})[invitor] = {
            NAME: room_name,
            STATUS: rooms[room_name][STATUS],
            MESSAGE: message,
            GAME: rooms[room_name][GAME],
        }
    except Exception as e:
        print(f"Error during handle_send_invite: {e}")
        server_to_inviter.sendall(b"Invite handling failed.")


def handle_reply_invite(server_to_invitee, invitor, invitee, online_users, invitations, rooms):
    """
    Handles replying to an invitation from the invitee.
    """
    try:
        if invitee not in invitations or invitor not in invitations[invitee]:
            server_to_invitee.sendall(b"Reply error: Invitation not found in mailbox")
            return

        room_name = invitations[invitee][invitor][NAME]

        if len(rooms[room_name][PLAYERS]) >= MAX_PLAYERS:
            server_to_invitee.sendall(b"Reply failed: Room is already full")
            return

        game_type = invitations[invitee][invitor][GAME]
        server_to_invitee.sendall(f"Success {game_type}".encode())

        check_and_sending_game(server_to_invitee, game_type)

        rooms[room_name][PLAYERS].append(invitee)
        online_users[invitee][STATUS] = IN_ROOM

        del invitations[invitee][invitor]
    except Exception as e:
        print(f"Error during handle_reply_invite: {e}")
        server_to_invitee.sendall(b"Reply handling failed due to an internal error")
