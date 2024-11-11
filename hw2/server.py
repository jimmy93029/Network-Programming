import threading
from utils.connection import bind_server
from lobby import handle_register, handle_login1, handle_login2, handle_logout, handle_display
from room import handle_create_room, handle_invite1, handle_invite2, handle_invite3, handle_join1, handle_join2
from game import handle_game_start, handle_game_ending


user_db = {}        # key : user name, value = password
online_users = {}   # key : user name, value(dict) = status, socket
rooms = {}          # key : room id, value(dict) = creator, game type, room type, *participant and room status
login_addr = {}     # key : addr, value = username
mailbox = {}        # key : invitee, value = inviter

def run():
    server_socket = bind_server()
    assert server_socket is not None, "server_socket is not initialized"

    while True:
        # accept client connection
        client, addr = server_socket.accept()
        print(f"Connected by {addr}")

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client, addr))
        client_thread.start()


def handle_client(client, addr):
    try:
        while True:
            data = client.recv(1024).decode()  

            exit = handle(data, client, addr)
            if exit:
                break
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client.close()


def handle(data, client, addr):
    exit = False
    if data != "":
        print(f"{addr} : {data}")

    # lobby related    
    if data.startswith("REGISTER"):
        handle_register(data, client, addr, user_db)
    elif data.startswith("LOGIN1"):
        exit = handle_login1(data, client, addr, user_db, login_addr)
    elif data.startswith("LOGIN2"):
        exit = handle_login2(data, client, addr, user_db, login_addr, online_users)
    elif data.startswith("LOGOUT"):
        exit = handle_logout(data, client, addr, login_addr, online_users)
    elif data.startswith("DISPLAY"):
        handle_display(data, client, addr, online_users, rooms)

    # room related
    if data.startswith("CREATE"):
        handle_create_room(data, client, addr, rooms, login_addr, online_users)
    elif data.startswith("INVITE1"):
        handle_invite1(data, client, addr, login_addr, online_users, mailbox)
    elif data.startswith("INVITE2"):
        handle_invite2(data, client, addr, login_addr, online_users, mailbox)
    elif data.startswith("INVITE3"):
        handle_invite3(data, client, addr, login_addr, online_users, rooms, mailbox)
    elif data.startswith("JOIN1"):
        handle_join1(data, client, addr, rooms, online_users, login_addr)
    elif data.startswith("JOIN2"):
        handle_join2(data, client, addr, rooms, online_users, login_addr)

    # game related
    if data.startswith("FINISH"):
        handle_game_ending(data, client, addr, rooms, login_addr, online_users)
    elif data.startswith("START"):  
        handle_game_start(data, client, addr, rooms, login_addr, online_users)

    return exit


if __name__ == "__main__":
    run()
