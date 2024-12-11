import threading
from lobby import (
    do_listing_online_players, do_listing_available_players, do_listing_rooms,
    do_listing_invitations, do_register, do_login, do_logout
)
from room import (
    do_create_room, do_invite, do_join_room, do_reply_invitation,
    do_host_leave, do_player_waiting
)
from game import (
    do_starting_game1, do_starting_game2, do_upload_game,
    do_listing_all_game, do_listing_my_game
)
from utils.connection import connect_to_server
from utils.tools import client_init
from utils.variables import (
    UNLOGIN, IDLE, EXIT, GAME_DEVOPLOP, INVITE_MANAGE, INVITE_SENDING,
    IN_ROOM_HOST, IN_ROOM_PLAYER, IN_GAME_PLAYER
)
from utils.boardcast import listen_for_broadcasts, get_user_input
import time


client_socket = None  # client for user to connect to server
option = None         # user option
broadcast_thread = None  # Broadcast thread


def run():
    global client_socket
    global broadcast_thread

    status = UNLOGIN
    client_init()

    while True:
        try:
            question(status)
            status = do(status)

            if status == EXIT:
                break

            print("------------------------------------------------------------------\n")

        except KeyboardInterrupt:
            print("Disconnected due to KeyboardInterrupt")
            if client_socket:
                do_logout(client_socket, retry=1)
                client_socket.close()
                client_socket = None
            break
        except (ConnectionError, BrokenPipeError):
            print("Server is down or connection lost. Exiting...")
            if client_socket:
                client_socket.close()
                client_socket = None
            break


def question(status):
    global option
    prompt_list = None
    stop_event = threading.Event()

    # Define the available options based on the current status
    if status == UNLOGIN:
        prompt_list = ["Login", "Register", "Exit"]
    elif status == IDLE:
        prompt_list = [
            "Create gaming room", "Join gaming room", "List all online players",
            "List all online rooms", "Invitation management", "List all games",
            "Game Develop Management", "Logout"
        ]
    elif status == GAME_DEVOPLOP:
        prompt_list = ["List your games", "Publish the game", "Back to lobby"]
    elif status == INVITE_MANAGE:
        prompt_list = ["List all the requests", "Accept request", "Back to lobby"]
    elif status in [IN_ROOM_PLAYER, IN_GAME_PLAYER]:
        return None
    elif status == IN_ROOM_HOST:
        prompt_list = ["Invite Player", "Start Game", "Leave the room"]
    elif status == INVITE_SENDING:
        prompt_list = ["List available players", "Invite player", "Back to room"]
    else:
        return None

    # Start the input thread to gather user input
    input_thread = threading.Thread(target=get_user_input, args=(prompt_list, set_option))
    input_thread.start()

    # Start the broadcast thread if not already running
    broadcast_thread = threading.Thread(target=listen_for_broadcasts, args=(client_socket, stop_event), daemon=True)
    broadcast_thread.start()

    # Wait for the input thread to complete and signal the broadcast thread to stop
    input_thread.join()
    stop_event.set()
    broadcast_thread.join()


def do(status):
    global client_socket
    status_ = None

    if status == UNLOGIN:
        if option == 1:
            client_socket = connect_to_server()
            status_ = do_login(client_socket)
            if status_ is None:
                client_socket.close()
                client_socket = None
        elif option == 2:
            do_register()
        elif option == 3:
            status_ = EXIT

    elif status == GAME_DEVOPLOP:
        if option == 1:
            do_listing_my_game()
        elif option == 2:
            do_upload_game(client_socket)
        elif option == 3:
            status_ = IDLE

    elif status == INVITE_MANAGE:
        if option == 1:
            do_listing_invitations(client_socket)
        elif option == 2:
            status_ = do_reply_invitation(client_socket)
        elif option == 3:
            status_ = IDLE

    elif status == IDLE:
        if option == 1:
            status_ = do_create_room(client_socket)
        elif option == 2:
            status_ = do_join_room(client_socket)
        elif option == 3:
            do_listing_online_players(client_socket)
        elif option == 4:
            status_ = do_listing_rooms(client_socket)
        elif option == 5:
            status_ = INVITE_MANAGE
        elif option == 6:
            do_listing_all_game(client_socket)
        elif option == 7:
            status_ = GAME_DEVOPLOP
        elif option == 8:
            status_ = do_logout(client_socket)
            if status_ is not None:
                client_socket.close()
                client_socket = None

    elif status == IN_ROOM_HOST:
        if option == 1:
            status_ = INVITE_SENDING
        elif option == 2:
            status_ = do_starting_game1(client_socket)
        elif option == 3:
            status_ = do_host_leave(client_socket)

    elif status == INVITE_SENDING:
        if option == 1:
            do_listing_available_players(client_socket)
        elif option == 2:
            do_invite(client_socket)
        elif option == 3:
            status_ = IN_ROOM_HOST

    elif status == IN_ROOM_PLAYER:
        status_ = do_player_waiting(client_socket)

    elif status == IN_GAME_PLAYER:
        status_ = do_starting_game2(client_socket)

    return status if status_ is None else status_


def set_option(value):
    """
    Callback function to set the selected option from user input.
    """
    global option
    option = value


if __name__ == "__main__":
    run()
