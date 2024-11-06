from lobby import do_display, do_register, do_login, do_display
from connection import connect_to_server


client_socket = None    # client for user to connect to server
game_socket1 = None     # game socket controlled by room creator
addr2 = None            # game addr for connecting to game server

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
                    (5) Renew screen"
        
    option = ""
    while not option.isdigit():
        option = input(prompt)
        print("Please input the options in number format!")
        
    return option
        

def do(option, status):
    global client_socket
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
            do_create_room(client_socket)

        elif int(option) == 2:
            status_, addr2 = do_join_room(client_socket)

        elif int(option) == 3:
            status, addr2 = wait_for_invitation(client_socket)

        elif int(option) == 4:
            status_ = do_logout(client_socket)
            if status_ is not None:
                client_socket.close()
        else:
            pass

    if status.startswith("In Room"):
        if status == "In Room private":
            status_, game_socket1 = do_invite(client_socket)
        elif status == "In Room public":
            status_, game_socket1 = wait_for_join(client_socket)

    if status.startswith("In Game"):
        if status == "In Game mode1":
            status_ = start_game1(game_socket1)
        if status == "In Game mode2":
            status_ = start_game2(addr2)            
        

    return status if status_ is None else status_


# Display online status 
def predo(status):
    if status == "login":
        do_display(client_socket)


if __name__ == "__main__":
    run()