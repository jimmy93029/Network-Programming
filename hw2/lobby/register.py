from ..connection import connect_to_server


""" Client """
def do_register(client):
    try:
        client_socket = connect_to_server()

        username = input("Enter a username for registration: ")
        password = input("Enter a password for registration: ")

        # The player enters a username and a password.
        message = f"REGISTER {username} {password}"
        client.sendall(message.encode())
        
        response = client.recv(1024).decode()
        print("Server response:", response)

        client_socket.close()

    except (ConnectionError, TimeoutError) as e:
        print(f"Register failed due to network issue: {e}")


def handle_register(data, client, user_db):
    _, username, password = data.split()  
    
    # The game lobby server verifies whether the username already exists.
    if username in user_db:
        client.sendall("Username already exists.\n \
                        please enter another username for registration.".encode())
        return False
    else:
        # If the username does not exist, the game lobby server will store the username and password.
        user_db[username] = password
        client.sendall("Registration successful".encode())
        return False


# 還沒處理 exception
