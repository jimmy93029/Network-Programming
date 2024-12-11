from utils.tools import select_type 
from utils.boardcast import broadcast


""" Client """
def do_logout(client_socket, retry=1):
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
        if not retry:
            retry_logout(client_socket)


def retry_logout(client_socket):
    print("Do you want to retry? (yes/no):")
    options = ['yes', 'no']
    idx = select_type("retry optinos", options)

    if options[idx-1] == "yes":
        do_logout(client_socket, retry=1)
    else:
        print("Logout cancelled.")


""" Server """
def handle_logout(data, client, addr, login_addr, online_users, mailbox):
    try:
        # The player's status is removed, and they are deleted from the online players list
        username = login_addr[addr]
        del online_users[username]
        client.sendall("Logout successfully Bye Bye".encode())
        broadcast(online_users, f"{username} has logged out...", mailbox)

    except Exception as e:
        print(f"Server encountered an error during logout: {e}")
        client.sendall("Logout failed: Server error.".encode())


# 要怎麼處理 extention 登入失敗? 
