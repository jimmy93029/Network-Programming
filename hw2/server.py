import threading
from connection import bind_server
from lobby import handle_register, handle_login1, handle_login2, handle_logout, handle_display
from room import handle_create_room, handle_invite, handle_join

user_db = {}        # key : user name, value = password
online_users = {}   # key : user name, value = status, socket
rooms = {}          # key : room id, value = the creator, game type, room type, and room status
login_addr = {}     # key : addr, value = username


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
            data = client.recv(1024).decode()  # Decode instead of encode
            exit = handle(data, client, addr)
            if exit:
                break
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client.close()


def handle(data, client, addr):
    exit = False

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
        handle_display(data, client, addr)

    # room related
    if data.startswith("CREATE"):
        handle_create_room(data, client, addr, rooms, login_addr)
    elif data.startswith("INVITE"):
        handle_invite(data, client, addr, online_users, rooms)
    elif data.startswith("JOIN"):
        handle_join(data, client, addr, rooms, online_users)

    # game related
    if data.startwith("FINISH"):
        handle_game_ending()

    return exit

if __name__ == "__main__":
    run()
