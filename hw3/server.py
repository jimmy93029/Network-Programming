import threading
import os
from utils.connection import bind_server, handle_disconnected
from utils.variables import SERVER_FOLDER, GAME_META_FILE
from lobby import handle_register, handle_login1, handle_login2, handle_logout, handle_display
from room import handle_create_room, handle_invite1, handle_invite2, handle_invite3, handle_invite4, handle_join1, handle_join2
from game import handle_game_start, handle_game_ending, handle_list_all_games


user_db = {}        # key : user name, value = password
online_users = {}   # key : user name, value(dict) = {status, socket}
rooms = {}          # key : room id, value(dict) = {creator, game type, room type, *participant and status}
login_addr = {}     # key : addr, value = username
mailbox = {}        # key : invitee, value(list) = [list of messages]
invitations = {}    # key : invitee, value(dict) = {key : invitor, value(dict) = {room, room status, message} 
game_list = []      # entry: game_type
# games.csv         # row : GameName, Developer, Introduction 


def run():

    init()
    server_socket = bind_server()
    client_threads = []  # Track client threads and sockets
    
    try:
        while True:
            # Accept client connection
            client_socket, addr = server_socket.accept()
            print(f"Connected by {addr}")

            # Start a thread to handle this client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_threads.append((client_thread, client_socket))  # Store thread and socket
            client_thread.start()

    except KeyboardInterrupt:
        print("Shutting down server gracefully...")

        # Close all client connections and wait for threads to finish
        for thread, client_socket in client_threads:
            client_socket.close()  # Close client socket to notify them
            thread.join()  # Ensure each thread finishes cleanly
    finally:
        server_socket.close()  # Close the main server socket
        print("Server closed.")


def handle_client(client, addr):
    # Handle individual client connection
    try:
        while True:
            data = client.recv(1024).decode()
            exit = handle(data, client, addr)
            if exit:
                break
    except (BrokenPipeError, ConnectionResetError) as e:
        print(f"Connection lost with {addr}: {e}")
        handle_disconnected(client, addr)
    finally:
        client.close()  # Close client socket if loop ends or error occurs


def handle(data, client, addr):
    # Process client requests
    exit = False
    if data != "":
        print(f"{addr} : {data}")

    # Lobby commands
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

    # Room commands
    elif data.startswith("CREATE"):
        handle_create_room(data, client, addr, rooms, login_addr, online_users)

    elif data.startswith("INVITE"):
        if data.endswith("1"):
            handle_invite1(data, client, addr, login_addr, online_users, invitations )
        elif data.endswith("2"):
            handle_invite2(data, client, addr, login_addr, invitations)
        elif data.endswith("3"):
            handle_invite3(data, client, addr, login_addr, online_users, invitations)
        elif data.startswith("4"):
            handle_invite4(data, client, addr, login_addr, online_users, rooms, invitations)

    if data.startswith("JOIN"):
        if data.startswith("1"):
            handle_join1(data, client, addr, rooms, online_users, login_addr)
        elif data.startswith("2"):
            handle_join2(data, client, addr, rooms, online_users, login_addr)

    # Game commands
    elif data.startswith("LIST"):
        handle_list_all_games(data, client, addr)
    elif data.startswith("FINISH"):
        handle_game_ending(data, client, addr, rooms, login_addr, online_users)
    elif data.startswith("START"):  
        handle_game_start(data, client, addr, rooms, login_addr, online_users)

    return exit


def init():
    os.makedirs(SERVER_FOLDER, exist_ok=True)
    print(f"Directories '{SERVER_FOLDER}' ensured to exist.")

    if not os.path.exists(GAME_META_FILE):
        with open(GAME_META_FILE, 'w') as f:
            pass  # Create an empty file

    if not os.path.exists(GAME_META_FILE):
        with open(GAME_META_FILE, 'w') as f:
            pass  # Create an empty file


if __name__ == "__main__":
    run()
