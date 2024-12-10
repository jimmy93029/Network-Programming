import time
from utils.tools import select_type


def get_user_input(prompt_list, callback):
    """
    Handle user input in a separate thread.
    """
    user_option = select_type("prompts", prompt_list)
    callback(user_option)


def listen_for_broadcasts(client_socket):
    """
    Listen for broadcast messages from the server.
    """
    try:
        while True:
            # Check if the socket is valid
            if client_socket is None or client_socket.fileno() == -1:
                break

            # Request broadcast messages from the server
            client_socket.send(b"BROADCAST")
            response = client_socket.recv(4096).decode()
            if response and response != "no broadcast":
                print(f"\n[Broadcast] {response}")
            time.sleep(1)  # Reduce frequency to avoid server overload
    except Exception as e:
        print(f"Broadcast error: {e}")


def broadcast(online_users, message, mailbox, myself=None):
    """
    Send a broadcast message to all users in the lobby except the sender.
    """
    for username, _ in online_users.items():
        if username != myself:
            mailbox[username].append(message)


def handle_listen_for_broadcast(data, client, addr, mailbox, login_addr):
    """
    Handle broadcast listening request from a client.
    """
    username = login_addr[addr]
    if username not in mailbox:
        client.sendall(b"no broadcast")
        return

    # Check the user's broadcast mailbox
    if len(mailbox[username]):
        messages = "\n".join(mailbox[username])
        client.sendall(messages.encode())
        mailbox[username].clear()
    else:
        client.sendall(b"no broadcast")
