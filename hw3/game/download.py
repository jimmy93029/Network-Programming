import csv
import time
from utils.variables import LOCAL_GAME_META_FILE


def get_local_game_version(game_name, metadata_file):
    """
    Retrieves the game version from the specified metadata file.
    """
    try:
        with open(metadata_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['game_name'] == game_name:
                    return row['version'], row['filepath']
    except FileNotFoundError:
        print(f"Metadata file not found: {metadata_file}")
    return None, None


def check_and_update_game(client_socket, game_name):
    """
    Checks if the game version is up-to-date and downloads if necessary.
    """
    # Step 1: Get the local game version
    local_version = get_local_game_version(game_name)
    if local_version is None:
        print(f"No local version found for {game_name}. Requesting latest version.")
        local_version = "0"  # Assume no version

    # Step 2: Send the local version to the server
    client_socket.sendall(f"GAME_VERSION {game_name} {local_version}".encode())

    # Step 3: Receive the server's response
    response = client_socket.recv(1024).decode()
    if response == "Game version up-to-date":
        print(f"{game_name} is up-to-date.")
    elif response == "Game version outdated":
        print(f"{game_name} is outdated. Downloading the latest version...")
        receive_game_file(client_socket, f"game_folder/{game_name}.py")
    else:
        print("Unexpected response from server.")


def receive_game_file(client_socket, file_path):
    """
    Receives the updated game file from the server.
    """
    with open(file_path, 'wb') as f:
        while chunk := client_socket.recv(1024):
            f.write(chunk)
    print(f"Game {file_path} updated successfully.")


def check_and_sending_game(client, game_name):
    """
    Handles game version checks and sends updates if necessary.
    """
    # Step 2: Receive the client's game version
    version_request = client.recv(1024).decode()
    _, game_name, client_version = version_request.split()
    server_version, server_filepath = get_local_game_version(game_name, LOCAL_GAME_META_FILE)

    # Step 2: Compare versions and respond
    if client_version == server_version:
        client.sendall(b"Game version up-to-date")
    else:
        client.sendall(b"Game version outdated")

        # Step 3: Wait 3 seconds and send the game file
        time.sleep(3)
        send_game_file(client, server_filepath)


def send_game_file(client, file_path):
    """
    Sends the game file to the client.
    """
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024):
                client.sendall(chunk)
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")


