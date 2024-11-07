

""" Client """
def do_logout(client_socket):
    try:
        client_socket.sendall(b"LOGOUT")   
        response = client_socket.recv(1024).decode()

        print(response)
        if response.startswith("Logout successfully"):
            # The system confirms a successful logout and displays a logout message to the player.
            return "unlogin"
        else:
            retry_logout(client_socket)
        
    except (ConnectionError, TimeoutError) as e:
        print(f"Logout failed due to network issue: {e}")

        # The player can choose to retry logging out.
        retry_logout(client_socket)


def retry_logout(client_socket):
    while True:
        retry = input("Do you want to retry? (yes/no): ")
        if retry.lower() == "yes":
            do_logout(client_socket)
            break
        elif retry.lower() == "no":
            print("Logout cancelled.")
            break
        else:
            print("Invalid input. Please type 'yes' or 'no'.")


""" Server """
def handle_logout(data, client, addr, login_addr, online_users):
    try:
        # The player's status is removed, and they are deleted from the online players list
        username = login_addr[addr]
        del online_users[username]
        client.sendall("Logout successfully Bye Bye".encode())

    except Exception as e:
        print(f"Server encountered an error during logout: {e}")
        client.sendall("Logout failed: Server error.".encode())


# 要怎麼處理 extention 登入失敗? 
