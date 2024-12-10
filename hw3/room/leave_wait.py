import threading
from utils.tools import select_type
from utils.variables import IN_ROOM, IN_ROOM_HOST, IN_ROOM_PLAYER, IDLE, HOST, STATUS, PLAYERS, SOCKET


def do_host_leave(client_socket):
    """
    Handles the host leaving the room.
    """
    try:
        client_socket.sendall(b"LEAVE HOST")
        response = client_socket.recv(1024).decode()

        if response == "LEAVE_SUCCESS":
            print("You have left the room.")
            return IDLE
        else:
            print(f"Unexpected response: {response}")
            return IN_ROOM_HOST
    except Exception as e:
        print(f"Error during host leave: {e}")
        return IN_ROOM_HOST


def do_player_waiting(client_socket):
    """
    Handles player waiting in the room.
    Opens threads for user input and server communication.
    """
    def listen_to_server():
        """
        Listens for server messages.
        """
        nonlocal status
        while not exit_event.is_set():
            try:
                data = client_socket.recv(1024).decode()
                if data == "GAME_START":
                    print("Game is starting...")
                    status = IN_ROOM_PLAYER
                    exit_event.set()
                elif data == "HOST_LEAVE":
                    print("Host has left. You are now the host of the room.")
                    status = IN_ROOM_HOST
                    exit_event.set()
            except Exception as e:
                print(f"Error while receiving server data: {e}")
                exit_event.set()
                break

    def wait_for_user_input():
        """
        Waits for user input to leave the room.
        """
        nonlocal status
        print("You can choose to leave the room.")
        options = ["Leave Room"]
        choice = select_type("Choose an action", options)
        if choice == 1:  # Leave Room
            client_socket.sendall(b"LEAVE PLAYER")
            status = IDLE
            exit_event.set()

    # Create threads for listening and user input
    status = None
    exit_event = threading.Event()
    server_thread = threading.Thread(target=listen_to_server, daemon=True)
    input_thread = threading.Thread(target=wait_for_user_input, daemon=True)

    # Start threads
    server_thread.start()
    input_thread.start()

    # Wait for the exit event to be set
    exit_event.wait()

    # Ensure the threads terminate
    server_thread.join(timeout=1)
    input_thread.join(timeout=1)

    return status



""" Server """
def handle_leave(data, client, addr, rooms, login_addr, online_users):
    """
    Handles both host and player leave requests.
    """
    _, option = data.split()
    username = login_addr[addr]

    if option == "HOST":
        handle_host_leave(client, rooms, username, online_users)
    elif option == "PLAYER":
        handle_player_leave(client, rooms, username, online_users)


def handle_host_leave(client, rooms, username, online_users):
    """
    Handles the host leaving the room.
    """
    room_name = next(key for key, info in rooms.items() if info[HOST] == username)

    if not rooms[room_name][PLAYERS]:
        # No participants to promote to host
        del rooms[room_name]
        client.sendall(b"LEAVE_SUCCESS")
        online_users[username][STATUS] = IDLE
    else:
        # Promote a participant to host
        new_host = rooms[room_name][PLAYERS].pop(0)
        rooms[room_name][HOST] = new_host
        online_users[new_host][STATUS] = IN_ROOM
        online_users[username][STATUS] = IDLE

        client.sendall(b"LEAVE_SUCCESS")
        participant_socket = online_users[new_host][SOCKET]
        participant_socket.sendall(b"HOST_LEAVE")


def handle_player_leave(client, rooms, username, online_users):
    """
    Handles a player leaving the room.
    """
    room_name = next(key for key, info in rooms.items() if username in info[PLAYERS])
    rooms[room_name][PLAYERS].remove(username)
    online_users[username][STATUS] = IDLE
    client.sendall(b"LEAVE_SUCCESS")
