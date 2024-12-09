from lobby import do_listing_online_players, do_listing_available_players, do_listing_rooms, do_listing_invitations, do_register, do_login, do_logout
from room import do_create_room, do_invite, do_join_room, do_reply_invitation, do_host_leave, do_player_waiting
from game import do_starting_game1, do_starting_game2, do_upload_game, do_listing_all_game, do_listing_my_game
from utils.connection import connect_to_server
from utils.tools import select_type
from utils.variables import UNLOGIN, IDLE, EXIT, GAME_DEVOPLOP, INVITE_MANAGE, INVITE_SENDING, IN_ROOM_HOST, IN_ROOM_PLAYER, IN_GAME_PLAYER, client_init
from utils.boardcast import listen_for_broadcasts, get_user_input
import threading


client_socket = None    # client for user to connect to server
option = None           # 


def run():
    global client_socket
    status = UNLOGIN
    client_init()

    while True:
        try:
            option = question(status)
            status = do(option, status)
            if status == EXIT:
                break

            print("------------------------------------------------------------------\n")

        except KeyboardInterrupt:
            print("Disconnected due to KeyboardInterrupt")
            if client_socket:
                do_logout(client_socket, retry=1)
                client_socket.close()
            break
        except (ConnectionError, BrokenPipeError):
            print("Server is down or connection lost. Exiting...")
            if client_socket: client_socket.close()
            break


def question(status):
    prompt_list = None

    if status == UNLOGIN:
        prompt_list = ["Login", "Register", "Exit"]
    elif status == IDLE:
        prompt_list = ["Create gaming room", "Join gaming room", "List all online player", "List all online room", 
                        "Invitation management", "List all game", "Game Develop Management", "Logout"]
    elif status == GAME_DEVOPLOP:
        prompt_list = ["List your games", "publish the game", "Back to lobby"]
    elif status == INVITE_MANAGE:
        prompt_list = ["List all the requests", "Accept request", "Back to lobby"]
    elif status == IN_ROOM_HOST:
        prompt_list = ["Invite Player", "Start Game", "Leave the room"]
    elif status == INVITE_SENDING:
        prompt_list = ["List available player", "Invite player", "back to room"]
    elif status == IN_ROOM_PLAYER:
        return
    elif status == IN_GAME_PLAYER:
        return
    else:
        return
    
    if prompt_list:
        option = select_type("prompts", prompt_list)
        input_thread = threading.Thread(target=get_user_input, args=(prompt_list, set_option))
        broadcast_thread = threading.Thread(target=listen_for_broadcasts, daemon=True)

        broadcast_thread.start()
        input_thread.start()

        input_thread.join()
        
    return option, prompt_list
        

def do(option, status):
    global client_socket, game_socket1, game_type, game_addr
    status_ = None
    
    if status == UNLOGIN:
        if option == 1:
            client_socket = connect_to_server()
            status_ = do_login(client_socket)
            client_socket.close() if status_ is None else None
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
            status_, game_addr, game_type = do_join_room(client_socket)
        elif option == 3:
            do_listing_online_players(client_socket)
        elif option == 4:
            do_create_room(client_socket)
        elif option == 5:
            status_ = INVITE_MANAGE
        elif option == 6:
            do_listing_all_game(client_socket)
        elif option == 7:
            status_ = GAME_DEVOPLOP
        elif option == 8:
            status_ = do_logout(client_socket)
            client_socket.close() if status_ is not None else None
            
    elif status == IN_ROOM_HOST:
        if option == 1:
            status_ = INVITE_SENDING
        elif option == 2:
            status_ = do_starting_game1(client_socket)
        elif option == 3:
            do_host_leave(client_socket)
    
    elif status == INVITE_SENDING:
        if option == 1:
            do_listing_available_players(client_socket)
        elif option == 2:
            do_invite(client_socket)
        elif option == 3:
            status_ = IN_ROOM_HOST

    elif status == IN_ROOM_PLAYER:
        do_player_waiting(client_socket)

    elif status == IN_GAME_PLAYER:
        do_starting_game2(client_socket)

    return status if status_ is None else status_


def set_option(value):
    """
    Callback function to set the selected option from user input.
    """
    global option
    option = value


if __name__ == "__main__":
    run()
