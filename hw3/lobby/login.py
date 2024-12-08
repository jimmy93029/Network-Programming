

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
    if response == "User exist":
        return True
    elif response == "User does not exist":
        # The player receives an error prompt, unable to log in, and is advised to register.
        print("Please register first.")
        return False
    else:  # server problem

        return False
  

def login2(client_socket, retry=0):
    # If the username exists, the game lobby server prompts the player to enter their password.
    password = input("Enter your password to login: ") 
    message = f"LOGIN2 {password} {retry}"
    client_socket.sendall(message.encode())

    response = client_socket.recv(1024).decode()
    if response == "Login successful":
        print("Logging successfully")
        return "idle"
    elif not retry:
        # The player receives an error prompt and tries to log in again.
        print("Incorrect password. Please retry again")
        return login2(client_socket, retry=1)
    else:
        print("Incorrect password twice. Maybe login later")


""" Sever """
def handle_login1(data, client, addr, user_db, login_addr):
    try:
        _, username = data.split()  # The player enters the username.

        # The game lobby server verifies whether the username exists.
        if username not in user_db:
            # The game lobby server discovers that the player is not 
            # registered and responds with the error message: "User does not exist."
            client.sendall("User does not exist".encode())
            return True
        else:
            login_addr[addr] = username
            client.sendall("User exist".encode())
            return False

    except Exception as e:
        print(f"Server encountered an error during login1: {e}")
        client.sendall("Login1 failed: Server error.".encode())
        return True


def handle_login2(data, client, addr, user_db, login_addr, online_users, mailbox):
    try:
        _, password, retry = data.split()  # The game lobby server prompts the player to enter their password.
        username = login_addr.get(addr)

        if not username:
            client.sendall("Session error: please re-login.".encode())
            return True

        # The game lobby server verifies the correctness of the password.
        if user_db.get(username) == password:
            online_users[username] = {"status": "idle", "socket": client}
            mailbox[username] = []
            client.sendall("Login successful".encode())
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
