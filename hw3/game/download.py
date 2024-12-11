import time
from utils.variables import LOCAL_GAME_META_FILE, GAME_NAME, VERSION
from utils.fileIO import receive_file, send_file, get_csv_data


def update_game(client_socket, game_name):
    """
    Checks if the game version is up-to-date and downloads if necessary.
    """
    # Step 1: Get the local game version
    local_game = get_csv_data(LOCAL_GAME_META_FILE, key=GAME_NAME, value=game_name)
    if local_game is None:
        print(f"No local version found for {game_name}. Requesting latest version.")
        local_version = "0"  # Assume no version
    else:
        local_version = local_game[VERSION]

    # Step 2: Send the local version to the server
    client_socket.sendall(f"VERSION {local_version} {game_name}".encode())
    file_path = f"{game_name}.py"

    # Step 3: Receive the server's response
    response = client_socket.recv(1024).decode()
    if response == "Game version up-to-date":
        print(f"{game_name} is up-to-date.")
    elif response == "Game version outdated":
        print(f"{game_name} is outdated. Downloading the latest version...")
        receive_file(client_socket, file_path)
    else:
        print("Unexpected response from server.")
        print(f"response : {response}")


def handle_update_game(data, client, addr):
    """
    Handles game version checks and sends updates if necessary.
    """
    # Step 1: Receive the client's game version
    _, client_version, game_name = data.split()

    game = get_csv_data(LOCAL_GAME_META_FILE, key=GAME_NAME, value=game_name)
    server_version = game[VERSION]
    file_path = f"{game_name}.py"

    # Step 2: Compare versions and respond
    if client_version == server_version:
        client.sendall(b"Game version up-to-date")
    else:
        client.sendall(b"Game version outdated")

        # Step 3: Wait 3 seconds and send the game file
        send_file(client, file_path)

