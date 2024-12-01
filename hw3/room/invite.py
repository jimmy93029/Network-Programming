from utils.connection import create_game_server
from utils.tools import select_type
from utils.variables import HOST, JOINER
import time


"""Client A"""
def do_invite(client_socket):
    invitee = input("Which idle user do you want to choose: ")
    client_socket.sendall(f"INVITE1 {invitee}".encode())
    print("Waiting for response...")

    response = client_socket.recv(1024).decode()
    print(response)
    if response != "accepted":
        return None, None
    
    try:
        game_socket1, ip_address, port = create_game_server()
        client_socket.sendall(f"INVITE4 {ip_address},{port}".encode())
        time.sleep(3)
        return HOST, game_socket1
    except:
        client_socket.sendall(b"STARTUP_FAILED")
        time.sleep(3)
        return None, None


"""Client B"""
def check_invitation(client_socket):
    # Step 1 : check if I am invited
    client_socket.sendall(b"INVITE2")
    check = client_socket.recv(1024).decode()
    print(check)
    if check == "you are not invited":
        return None, None, None

    # Step2 : decline or not
    answers = ["yes", "no"]
    idx = select_type("choices", answers)

    if answers[idx-1] == "yes":
        client_socket.sendall("INVITE3 accepted".encode())
    else:
        client_socket.sendall("INVITE3 declined".encode())
        return None, None, None
    
    # Step3 : update game
    client_socket.sendall(f"INVITE5 {} {}".encode())

    # Step 4 : acquire game ip address
    message = client_socket.recv(1024).decode()

    if message == "STARTUP_FAILED":
        print("Game server failed to start.")
        return None, None, None
    else:
        ip_address, port, game_type = message.split(",")
        game_addr = (ip_address, int(port))
        time.sleep(3)
        return JOINER, game_addr, game_type


"""Server"""
def handle_invite1(data, client, addr, login_addr, online_users, mailbox):
    try:
        _, invitee = data.split()
        inviter = login_addr[addr]

        # check invitee
        if invitee not in online_users:
            client.sendall(b"Invite failed: Invitee is not connected")
            return
        elif online_users[invitee]["status"] != "idle":
            client.sendall(b"Invite failed: User is not idle")
            return

        # record invitation
        mailbox[invitee] = inviter

    except Exception as e:
        print(f"Error during handling invite1: {e}")
        client.sendall(b"Invite handling failed.")


def handle_invite2(data, client, addr, login_addr, mailbox):
    try:
        invitee = login_addr[addr]

        if invitee not in mailbox:
            client.sendall(b"you are not invited")
            return
        else:
            inviter = mailbox[invitee]
            client.sendall(f"You have been invited by {inviter}. Do you accept the invitation?".encode())

    except Exception as e:
        print(f"Error during handling invite2: {e}")


def handle_invite3(data, client, addr, login_addr, online_users, mailbox):
    try:
        _, reply = data.split()

        invitee = login_addr[addr]
        inviter = mailbox[invitee]
        inviter_socket = online_users[inviter]["socket"]

        # process invitation response
        if reply == "declined":
            inviter_socket.sendall(b"declined")
            del mailbox[invitee]  # clear mailbox entry after declining
        else:
            inviter_socket.sendall(b"accepted")

    except Exception as e:
        print(f"Error during handling invite3: {e}")


def handle_invite4(data, server_to_inviter, addr, login_addr, online_users, rooms, mailbox):
    try:
        _, message = data.split(maxsplit=1)

        inviter = login_addr[addr]
        invitee = next((key for key, info in mailbox.items() if info == inviter), None)
        server_to_invitee = online_users[invitee]["socket"]
        roomId = next((key for key, info in rooms.items() if info["creator"] == inviter), None)
        game_type = rooms[roomId]["game_type"]
        del mailbox[invitee]

        # check game server startup status
        if message.startswith("STARTUP_FAILED"):
            server_to_invitee.sendall(b"STARTUP_FAILED")
            return
        else:
            ip_address, port = message.split(",")
            server_to_invitee.sendall(f"{ip_address},{port},{game_type}".encode())

        # update room and user status
        rooms[roomId]["status"] = "In Game"
        rooms[roomId]["participant"] = invitee
        online_users[inviter]["status"] = "In Game"
        online_users[invitee]["status"] = "In Game"
        
    except Exception as e:
        print(f"Error during handling invite4: {e}")
