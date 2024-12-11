import threading
import sys
import select
import time
from utils.variables import IN_ROOM, IN_ROOM_HOST, IN_GAME_PLAYER, IDLE, HOST, STATUS, PLAYERS, SOCKET


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
    Opens threads for non-blocking input and server communication.
    """
    def listen_to_server():
        """
        Listens for server messages from the server.
        """
        nonlocal status
        while not exit_event.is_set():
            try:
                data = client_socket.recv(1024).decode()
                if data == "GAME_START":
                    print("Game is starting...")
                    update_status(IN_GAME_PLAYER)
                    exit_event.set()
                elif data == "HOST_LEAVE":
                    print("Host has left. You are now the host of the room.")
                    update_status(IN_ROOM_HOST)
                    exit_event.set()
            except Exception as e:
                print(f"Error while receiving server data: {e}")
                exit_event.set()
                break

    def non_blocking_input():
        """
        Continuously checks for user input to leave the room.
        """
        nonlocal status
        print("Input anything if you want to leave the room : ")
        while not exit_event.is_set():
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:  # Check if input is ready
                user_input = sys.stdin.readline().strip()
                if user_input:  # User entered something
                    client_socket.sendall(b"LEAVE PLAYER")
                    update_status(IDLE)
                    exit_event.set()
                    break

    def update_status(new_status):
        """
        Thread-safe update to status variable.
        """
        nonlocal status
        with status_lock:
            status = new_status

    # Thread-safe status and exit event
    status = None
    exit_event = threading.Event()
    status_lock = threading.Lock()

    # Create and start threads
    server_thread = threading.Thread(target=listen_to_server)
    input_thread = threading.Thread(target=non_blocking_input)

    server_thread.start()
    input_thread.start()

    # Wait for the exit event to be set
    exit_event.wait()

    # Wait for threads to complete
    server_thread.join()
    input_thread.join()

    # Safely retrieve the final status
    with status_lock:
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
        time.sleep(2)
        online_users[username][STATUS] = IDLE
    else:
        # Promote a participant to host
        new_host = rooms[room_name][PLAYERS].pop(0)
        rooms[room_name][HOST] = new_host
        if new_host:
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
    time.sleep(2)
