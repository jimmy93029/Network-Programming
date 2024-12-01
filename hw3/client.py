from lobby import do_display, do_register, do_login, do_logout, do_showing_rooms, do_showing_players
from room import do_create_room, do_invite, do_join_room, check_invitation, wait_for_join
from game import start_game1, start_game2, do_listing_all_game, do_listing_my_game
from utils.connection import connect_to_server
from utils.tools import select_type
from utils.variables import UNLOGIN, IDLE, EXIT, GAME_DEVOPLOP, INVITE_MANAGE


client_socket = None    # client for user to connect to server
game_socket1 = None     # game socket controlled by room creator
game_type = None
game_addr = None            # game addr for connecting to game server

def run():
    global client_socket
    status = UNLOGIN

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
        prompt_list = ["List all the requests", "Accepte request", "Back to lobby"]
    elif status.startswith("In Room"):
        prompt_list = ["Invite Player", "Start Game (Host only)", "Leave the room"]
    else:
        return
    
    if prompt_list:
        option = select_type("prompts", prompt_list)
        
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
            pass
        elif option == 3:
            status_ = IDLE

    elif status == INVITE_MANAGE:
        if option == 1:
            pass
        elif option == 2:
            pass
        elif option == 3:
            status_ = IDLE

    elif status == IDLE:
        if option == 1:
            status_, game_type = do_create_room(client_socket)
        elif option == 2:
            status_, game_addr, game_type = do_join_room(client_socket)
        elif option == 3:
            do_showing_players(client_socket)
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
            
    elif status.startswith("In Room"):
        if status.endswith("private"):
            status_, game_socket1 = do_invite(client_socket)
        elif status.endswith("public"):
            status_, game_socket1 = wait_for_join(client_socket)

    elif status.startswith("In Game"):
        if status.endswith("host"):
            status_ = start_game1(client_socket, game_socket1, game_type)
        elif status.endswith("joiner"):
            status_ = start_game2(client_socket, game_addr, game_type)

    return status if status_ is None else status_


if __name__ == "__main__":
    run()