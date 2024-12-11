from .register import load_user_db
from utils.variables import IDLE
from utils.tools import user_init
from utils.boardcast import broadcast

""" Client """
def do_login(client_socket):
    try:
        status_ = None

        username_exist = login1(client_socket)
        if username_exist:
            status_ = login2(client_socket)

        return status_
    
    except (ConnectionError, TimeoutError) as e:
        print(f"Login failed due to network issue: {e}")


def login1(client_socket):
    # The player enters the username.
    username = input("Enter your username to login: ")
    message = f"LOGIN1 {username}"
    client_socket.sendall(message.encode())

    response = client_socket.recv(1024).decode()
    print(response)
    if response == "User exists":
        return True
    else:
        # The player receives an error prompt, unable to log in, and is advised to register.
        print(f"response : {response}")
        return False


def login2(client_socket, retry=0):
    # If the username exists, the game lobby server prompts the player to enter their password.
    password = input("Enter your password to login: ")
    message = f"LOGIN2 {password} {retry}"
    client_socket.sendall(message.encode())

    response = client_socket.recv(1024).decode()
    if response == "Login successful":
        print("Login successfully.")
        return IDLE
    elif not retry:
        # The player receives an error prompt and tries to log in again.
        print("Incorrect password. Please retry again.")
        return login2(client_socket, retry=1)
    else:
        print("Incorrect password twice. Please try logging in later.")
        return None


""" Server """
def handle_login1(data, client, addr, login_addr, online_users):
    try:
        _, username = data.split()  # The player enters the username.

        # Load user database
        user_db = load_user_db()

        # The game lobby server verifies whether the username exists.
        if username not in user_db:
            # The game lobby server responds with the error message: "User does not exist."
            client.sendall(b"User does not exist")
            return True
        elif username in online_users:
            client.sendall(b"User is already login")
            return True
        else:
            login_addr[addr] = username
            client.sendall(b"User exists")
            return False

    except Exception as e:
        print(f"Server encountered an error during login1: {e}")
        client.sendall("Login1 failed: Server error.".encode())
        return True


def handle_login2(data, client, addr, login_addr, online_users, mailbox, invitations):
    try:
        _, password, retry = data.split()  # The game lobby server prompts the player to enter their password.
        username = login_addr.get(addr)

        if not username:
            client.sendall("Session error: please re-login.".encode())
            return True

        # Load user database
        user_db = load_user_db()

        # The game lobby server verifies the correctness of the password.
        if user_db.get(username) == password:
            user_init(username, online_users, client, mailbox, invitations, addr)
            client.sendall("Login successful".encode())
            broadcast(online_users, f"{username} has logged in...", mailbox)
            return False
        elif not int(retry):
            # The game lobby server responds with the error message: "Incorrect password."
            client.sendall("Incorrect password".encode())
            return False
        else:
            client.sendall("Incorrect password twice".encode())
            return True

    except Exception as e:
        print(f"Server encountered an error during login2: {e}")
        client.sendall("Login2 failed: Server error.".encode())
        return True
