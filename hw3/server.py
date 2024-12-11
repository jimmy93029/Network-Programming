import threading
from utils.connection import bind_server, handle_disconnected
from utils.boardcast import handle_listen_for_broadcast
from utils.tools import server_init
from lobby import handle_register, handle_login1, handle_login2, handle_logout, handle_display
from room import handle_create_room, handle_invite, handle_join, handle_leave
from game import handle_game_issue, handle_list_all_games, handle_upload, handle_update_game


online_users = {}   # key : user name, value(dict) = {status, socket}
rooms = {}          # key : room id, value(dict) = {creator, game type, room type, *participant and status}
login_addr = {}     # key : addr, value = username
mailbox = {}        # key : invitee, value(list) = [list of messages]
invitations = {}    # key : invitee, value(dict) = {key : invitor, value(dict) = {room, room status, message} 
game_list = []      # entry: game_type
# games.csv         # row : GameName, Developer, Introduction 
# user_datas.csv    # row : username, password      


def run():
    server_socket = bind_server()
    client_threads = []  # Track client threads and sockets
    server_init(game_list)
    
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
        handle_register(data, client, addr)
    elif data.startswith("LOGIN1"):
        exit = handle_login1(data, client, addr, login_addr, online_users)
    elif data.startswith("LOGIN2"):
        exit = handle_login2(data, client, addr, login_addr, online_users, mailbox, invitations)
    elif data.startswith("LOGOUT"):
        exit = handle_logout(data, client, addr, login_addr, online_users, mailbox)
    elif data.startswith("DISPLAY"):
        handle_display(data, client, addr, login_addr, online_users, rooms, invitations)

    # Room commands
    elif data.startswith("CREATE"):
        handle_create_room(data, client, addr, rooms, login_addr, online_users, game_list, mailbox)
    elif data.startswith("INVITE"):
        handle_invite(data, client, addr, login_addr, online_users, invitations, rooms)
    elif data.startswith("JOIN"):
        handle_join(data, client, addr, rooms, online_users, login_addr)
    elif data.startswith("LEAVE"):    
        handle_leave(data, client, addr, rooms, login_addr, online_users)

    # Game commands
    if data.startswith("GAME"):
        handle_game_issue(data, client, addr, rooms, login_addr, online_users)
    elif data.startswith("UPLOAD"):
        handle_upload(data, client, addr, login_addr, game_list)
    elif data.startswith("LIST"):
        handle_list_all_games(data, client, addr)
    elif data.startswith("VERSION"):
        handle_update_game(data, client, addr)

    # Uitls commands
    if data.startswith("BROADCAST"):
        handle_listen_for_broadcast(data, client, addr, mailbox, login_addr)

    return exit


if __name__ == "__main__":
    run()
