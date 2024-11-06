import socket


HOST = '127.0.0.1'  # Server IP
PORT = 10001        # Port 


def bind_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
    return server_socket


def connect_to_server(addr=(HOST, PORT)):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(addr)
    return client_socket


def create_game_server():
    while True:
        try:
            # 建立一個 socket，使用系統自動選擇端口
            game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            game_socket.bind(('', 0))  # 自動選擇一個可用的 port
            game_socket.listen(5)

            ip_address, port = game_socket.getsockname()
            print(f"Game server is running on IP: {ip_address}, Port: {port}")

            return game_socket, ip_address, port  # 成功啟動時回傳伺服器資訊

        except OSError as e:
            # 捕捉端口被佔用或其他綁定錯誤
            print(f"Error starting game server: {e}")
            retry = input("Game server failed to start. Do you want to retry with a different port? (yes/no): ")
            if retry.lower() != 'yes':
                print("Game server setup aborted.")
                return None, None, None  # 若選擇不重試，則回傳 None 值來通知失敗