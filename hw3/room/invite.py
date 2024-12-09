from utils.variables import IN_ROOM_PLAYER, IN_ROOM, NAME, STATUS, MESSAGE, PLAYERS, GAME, HOST, IDLE
from game.download import check_and_update_game, check_and_sending_game


"""Client A"""
def do_invite(client_socket):
    invitee = input("Which idle user do you want to choose: ")
    message = input("What is your invitation message (don't write '|' in message): ")
    client_socket.sendall(f"INVITE SEND {invitee}|{message}".encode())

    response = client_socket.recv(1024).decode()
    if response.startswith("Invite failed"):
        print(response)


"""Client B"""
def do_reply_invitation(client_socket):
    """
    Handles replying to an invitation from an invitor in a 3-step communication process.
    """
    # Step 1: Send the invitor's name to the server
    invitor = input("Enter the name of the invitor to reply to: ")
    client_socket.sendall(f"INVITE REPLY {invitor}".encode())

    # Step 2: Receive the server's response
    response = client_socket.recv(1024).decode()
    if response.startswith("Reply error"):
        print(response)
        return
    elif response.startswith("Success"):
        _, game_type = response.split(" ")
        print(f"Invitation accepted! Game type: {game_type}")
    else:
        print("Unexpected response from server.")
        return

    # Step 2: Send the current game version to the server
    check_and_update_game(client_socket, game_type)

    # Final Step: Update client status to IN_ROOM_PLAYER
    print("You are now IN_ROOM_PLAYER.")
    
    return IN_ROOM_PLAYER


"""Server"""
def handle_invite(data, server_to_client, addr, login_addr, online_users, invitations, rooms):
    _, option, info = data.split()

    if option == "SEND":
        invitor = login_addr[addr]
        invitee, message = info.split("|")
        handle_send_invite(server_to_client, invitor, invitee, message, online_users, invitations, rooms)
    elif option == "REPLY":
        invitor = info
        invitee = login_addr[addr]
        handle_reply_invite(server_to_client, invitor, invitee, online_users, invitations, rooms)


def handle_send_invite(server_to_inviter, invitor, invitee, message, online_users, invitations, rooms):
    try:
        # check invitee
        if invitee not in online_users:
            server_to_inviter.sendall(b"Invite failed: Invitee is not connected")
            return
        elif online_users[invitee][STATUS] != IDLE:
            server_to_inviter.sendall(b"Invite failed: User is not idle")
            return

        room_name = next((key for key, info in rooms.items() if info[HOST] == invitor), None)
        # record invitation
        invitations[invitee][invitor] = {NAME:room_name, STATUS: rooms[room_name][STATUS], MESSAGE: message}

    except Exception as e:
        print(f"Error during handling invite1: {e}")
        server_to_inviter.sendall(b"Invite handling failed.")


def handle_reply_invite(server_to_invitee, invitor, invitee, online_users, invitations, rooms):
    """
    Handles a reply to an invitation from an invitee in a 3-step communication process.
    """
    # Step 1: Parse the invitor name from the request

    # Step 1: Check if the invitor exists in the invitee's mailbox
    if invitee not in invitations or invitor not in invitations[invitee]:
        server_to_invitee.sendall(b"Reply error: Invitation not found in mailbox")
        return

    # Step 1: Send success response with game type
    room_name = invitations[invitee][invitor][NAME]
    game_type = rooms[room_name][GAME]
    server_to_invitee.sendall(f"Success {game_type}".encode())

    # Step 2: Check and send game updates if necessary
    check_and_sending_game(server_to_invitee, game_type)

    # Final Step: Add the invitee to the room and update their status
    rooms[room_name][PLAYERS].append(invitee)
    online_users[invitee][STATUS] = IN_ROOM


