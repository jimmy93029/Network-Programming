
def get_game_metadata(game_name):
    """從 CSV 中取得遊戲元數據"""
    with open(GAME_META_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['game_name'] == game_name:
                return row
    return None


def check_and_download_game(user_folder, game_name):
    """檢查玩家資料夾中是否已有最新版本的遊戲，否則下載"""
    game_metadata = get_game_metadata(game_name)
    if not game_metadata:
        raise FileNotFoundError(f"Game {game_name} not found on the server.")

    game_path = game_metadata['filepath']
    user_game_path = os.path.join(user_folder, os.path.basename(game_path))

    # 如果遊戲版本一致，則不需要下載
    if os.path.exists(user_game_path):
        with open(user_game_path, 'r') as local_game, open(game_path, 'r') as server_game:
            if local_game.read() == server_game.read():
                print(f"{game_name} is up to date.")
                return

    # 將伺服器端的遊戲文件複製到玩家資料夾
    shutil.copy(game_path, user_game_path)
    print(f"Downloaded the latest version of {game_name} to {user_folder}.")


def download_game(client_socket, game_name):
    """從伺服器下載遊戲文件"""
    client_socket.send(f"DOWNLOAD {game_name}".encode())
    response = client_socket.recv(1024).decode()
    if response.startswith("ERROR"):
        print(response)
        return

    # 接收遊戲文件內容
    with open(f'game_folder/{game_name}.py', 'wb') as f:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            f.write(data)
    print(f"Game {game_name} downloaded successfully.")
