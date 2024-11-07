from lobby import do_display, do_register, do_login, do_logout, do_display
from room import do_create_room, do_invite, do_join_room, wait_for_invitation, wait_for_join
from game import start_game1, start_game2
from utils.connection import connect_to_server


client_socket = None    # client for user to connect to server
game_socket1 = None     # game socket controlled by room creator
game_type = None
game_addr = None            # game addr for connecting to game server

def run():
    global client_socket
    status = "unlogin"

    while True:
        predo(status)
        option = question(status)

        status = do(option, status)
        if status == "exit":
            break

        print("------------------------------------------------------------------\n")


def question(status):

    if status == "unlogin":
        prompt = "Which options do you want? \n\
                    (1) Login \n\
                    (2) Register \n\
                    (3) Exit  \n"
    elif status == "idle":
        prompt = "Which options do you want? \n\
                    (1) Create room \n\
                    (2) Join room \n\
                    (3) Wait for invitation\n\
                    (4) Logout\n\
                    (5) Renew screen\n"
    else:
        return
    prompt = prompt + "Plealse input your choose : "
        
    option = input(prompt)
    while not option.isdigit():
        print("Please input the options in number format!")
        option = input(prompt)
        
    return option
        

def do(option, status):
    global client_socket, game_socket1, game_type, game_addr
    status_ = None
    
    if status == "unlogin":
        if int(option) not in [1, 2, 3]:
            print("Please input the options in {1, 2}!")
        elif int(option) == 1:
            client_socket = connect_to_server()
            status_ = do_login(client_socket)
            if status_ is None:
                client_socket.close()
        elif int(option) == 2:
            do_register()
        elif int(option) == 3:
            status_ = "exit"

    elif status == "idle":
        if int(option) not in [1, 2, 3, 4, 5]:
            print("Please input the options in {1, 2, 3, 4}!")
        elif int(option) == 1:
            status_, game_type = do_create_room(client_socket)
        elif int(option) == 2:
            status_, game_addr, game_type = do_join_room(client_socket)
        elif int(option) == 3:
            status_, game_addr, game_type = wait_for_invitation(client_socket)
        elif int(option) == 4:
            status_ = do_logout(client_socket)
            if status_ is not None:
                client_socket.close()
        else:
            pass

    elif status.startswith("In Room"):
        if status.endswith("private"):
            status_, game_socket1 = do_invite(client_socket)
        elif status.endswith("public"):
            status_, game_socket1 = wait_for_join(client_socket)

    elif status.startswith("In Game"):
        if status.endswith("mode1"):
            status_ = start_game1(client_socket, game_socket1, game_type)
        elif status.endswith("mode2"):
            status_ = start_game2(client_socket, game_addr, game_type)

    # Return updated status or maintain current status if status_ is None
    return status if status_ is None else status_


# Display online status 
def predo(status):
    if status != "unlogin":
        do_display(client_socket)


if __name__ == "__main__":
    run()