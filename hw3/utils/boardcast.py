import threading
import time
from utils.tools import select_type

broadcast_event = threading.Event()


def get_user_input(prompt_list, callback):
    """
    Handle user input in a separate thread.
    """
    global broadcast_event

    user_option = select_type("prompts", prompt_list)
    callback(user_option)

    # 清除广播事件，停止广播线程
    broadcast_event.clear()


def listen_for_broadcasts(client_socket):
    """
    Listen for broadcast messages from the server.
    """
    while broadcast_event.is_set():  # 检查广播事件状态
        try:
            # 向服务器请求广播消息
            client_socket.send(b"BROADCAST")
            response = client_socket.recv(4096).decode()
            if response and response != "no broadcast":
                print(f"\n[Broadcast] {response}")
            time.sleep(1)  # 模拟接收广播间隔
        except Exception as e:
            print(f"Broadcast error: {e}")
            break


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

    # 检查该用户的广播信箱是否有消息
    if len(mailbox[username]):
        # 发送所有广播消息并清空信箱
        messages = "\n".join(mailbox[username])
        client.sendall(messages.encode())
        mailbox[username].clear()
    else:
        client.sendall(b"no broadcast")
