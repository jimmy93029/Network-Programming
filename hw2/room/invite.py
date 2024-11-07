from utils.connection import create_game_server


"""Client A"""
def do_invite(client_socket):
    invitee = input("Which idle user do you want to choose : ")
    client_socket.sendall(f"INVITE {invitee}".encode())

    response = client_socket.recv(1024).decode()
    print(response)
    if response == "declined":
        return 

    try:
        game_socket1, ip_address, port = create_game_server()
        client_socket.sendall(f"{ip_address} {port}".encode())
        return "In Game mode1", game_socket1
    except:
        client_socket.sendall(b"STARTUP_FAILED Room creator unable to start the game server")


"""Client B"""
def wait_for_invitation(client_socket):
    print("Waiting for an invitation...")
    while True:
        question = client_socket.recv(1024).decode()
        print(question)
        answer = input("Do you accept the invitation? (yes/no): ").strip().lower()
        client_socket.sendall(answer.encode())

        if answer == "no":
            print("You declined the invitation.")
            return 
        
        message  = client_socket.recv(1024).decode()
        if message == "STARTUP_FAILED":
            return
        else:
            ip_address, port, game_type = message 

        game_addr = (ip_address, int(port))
        return "In Game mode2", game_addr, game_type


"""Server"""
def handle_invite(data, client, addr, login_addr, online_users, rooms):
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
        invitee_socket.sendall(f"You have been invited by {inviter}.".encode())
        reply = invitee_socket.recv(1024).decode().strip()

        if reply.lower() == "no":
            client.sendall(f"declined".encode())
            return

        # give messages
        client.sendall(f"accepted".encode())
        message = client.recv(1024).decode()
        if message.startwith("STARTUP_FAILED"):
            invitee_socket.sendall("STARTUP_FAILED")
            return

        roomId = next((key for key, info in rooms.items() if info["creator"] == inviter), None)   
        game_type = rooms[roomId]["game_type"]
        ip_address, port = message  
        invitee_socket.sendall(f"{ip_address} {port} {game_type}")
    
        rooms[roomId]["status"] = "In Game"
        online_users[inviter]["status"] = "In Game"
        online_users[invitee]["status"] = "In Game"
        
    except Exception as e:
        print(f"Error during handling invite: {e}")


