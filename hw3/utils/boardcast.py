import time
from utils.tools import select_type


def get_user_input(prompt_list, callback):
    """
    Handle user input in a separate thread.
    """
    user_option = select_type("prompts", prompt_list)
    callback(user_option)

def listen_for_broadcasts(client_socket, stop_event):
    """
    Listen for broadcast messages from the server.
    Process complete messages and store incomplete parts in a buffer.
    """
    buffer = ""  # Initialize buffer to store incomplete messages
    try:
        while not stop_event.is_set():
            # Check if the socket is valid
            if client_socket is None or client_socket.fileno() == -1:
                break

            # Request broadcast messages from the server
            client_socket.send(b"BROADCAST")
            response = client_socket.recv(4096).decode()

            if response and response != "no broadcast":
                # Append the new response to the buffer
                buffer += response

                # Split messages by '|'
                parts = buffer.split('|')

                # Process all complete messages except the last part
                for message in parts[:-1]:
                    if message.strip():  # Ignore empty messages
                        print(message.strip())

                # Keep the last part in the buffer (it may be incomplete)
                buffer = parts[-1]

            time.sleep(0.5)  # Reduce frequency to avoid server overload
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
    Sends all messages in the mailbox prefixed with [Broadcast], separated by '|'.
    """
    username = login_addr[addr]
    if username not in mailbox or not mailbox[username]:
        client.sendall(b"no broadcast")
        return

    # Combine all messages with '[Broadcast]' prefix, separated by '|'
    messages = "|".join(f"[Broadcast] {message}" for message in mailbox[username])
    client.sendall((messages + "|").encode())  # Add a '|' at the end for completeness

    # Clear the mailbox after sending all messages
    mailbox[username].clear()
