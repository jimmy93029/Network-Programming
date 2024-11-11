from utils.connection import create_game_server
from utils.tools import select_type
import time

"""Client A"""
def do_invite(client_socket):
    invitee = input("Which idle user do you want to choose : ")
    client_socket.sendall(f"INVITE1 {invitee}".encode())

    response = client_socket.recv(1024).decode()
    print(response)
    if response != "accepted":
        return 

    try:
        game_socket1, ip_address, port = create_game_server()
        client_socket.sendall(f"INVITE3 {ip_address},{port}".encode())
        time.sleep(3)
        return "In Game mode1", game_socket1
    except:
        client_socket.sendall(b"STARTUP_FAILED")
        time.sleep(3)


"""Client B"""
def wait_for_invitation(client_socket):
    print("Waiting for an invitation...")

    question = client_socket.recv(1024).decode()
    print(question)
    inviter = question.strip()[-1]

    answers = ["yes", "no"]
    idx = select_type("choices", answers)

    if answers[idx-1] == "yes":
        client_socket.sendall(f"INVITE2 accepted {inviter}".encode())
    else:
        client_socket.sendall(f"INVITE2 declined {inviter}".encode())
        return 
    
    message  = client_socket.recv(1024).decode()
    if message == "STARTUP_FAILED":
        return
    else:
        ip_address, port, game_type = message 

    game_addr = (ip_address, int(port))
    return "In Game mode2", game_addr, game_type


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
            client.sendall(b"Invite is not idle ! Please invite anther one")

        # get invitee reply
        invitee_socket = online_users["socket"]
        mailbox[f"{invitee}"] = inviter

    except Exception as e:
        print(f"Error during handling invite: {e}")


def handle_invite2(data, client, addr, login_addr, online_users, mailbox):
    try:
        checker = login_addr[addr]
        if checker not in mailbox:
            return
        
        inviter = mailbox[checker]["inviter"]
        client.sendall(f"You have been invited by {inviter}. Do you accept the invitation?".encode())

        _ , reply, inviter = data.split()
        inviter_socket = online_users[inviter]["socket"]

        # check whether declined
        if reply == "declined":
            inviter_socket.sendall(f"declined".encode())
        else:
            inviter_socket.sendall(f"accepted".encode())
    except Exception as e:
        print(f"Error during handling invite: {e}")


def handle_invite3(data, server_to_inviter, addr, login_addr, online_users, rooms, mailbox):
    try:
        _, message = data.split()

        inviter = login_addr[addr]
        invitee = next((key for key, info in mailbox.items() if info == inviter), None)   
        server_to_invitee = online_users[invitee]["socket"]
        roomId = next((key for key, info in rooms.items() if info["creator"] == inviter), None)   
        game_type = rooms[roomId]["game_type"]

        # check whether startup failed
        if message.startwith("STARTUP_FAILED"):
            server_to_invitee.sendall("STARTUP_FAILED")
            return
        else:
            # give messages to joiner
            ip_address, port = message.split(",")
            server_to_invitee.sendall(f"{ip_address} {port} {game_type}")
    
        # change status
        rooms[roomId]["status"] = "In Game"
        rooms[roomId]["participant"] = invitee
        online_users[inviter]["status"] = "In Game"
        online_users[invitee]["status"] = "In Game"
        
    except Exception as e:
        print(f"Error during handling invite: {e}")