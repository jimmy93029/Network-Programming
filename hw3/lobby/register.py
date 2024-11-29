from utils.connection import connect_to_server


""" Client """
def do_register():
    try:
        client_socket = connect_to_server()

        username = input("Enter a username for registration: ")
        password = input("Enter a password for registration: ")

        # The player enters a username and a password.
        message = f"REGISTER {username} {password}"
        client_socket.sendall(message.encode())
        
        response = client_socket.recv(1024).decode()
        print("Server response:", response)

        client_socket.close()

    except (ConnectionError, TimeoutError) as e:
        print(f"Register failed due to network issue: {e}")


def handle_register(data, client, addr, user_db):
    _, username, password = data.split()  
    
    # The game lobby server verifies whether the username already exists.
    if username in user_db:
        message = "Username already exists.\n \
                   Please enter another username for registration."
        print(message)
        client.sendall(message.encode())
        return False
    else:
        # If the username does not exist, the game lobby server will store the username and password.
        user_db[username] = password
        message = "Registration successful"
        print(message)
        client.sendall(message.encode())
        return False


# 還沒處理 exception
