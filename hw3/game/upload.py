from utils.variables import LOCAL_GAME_META_FILE, GAME_NAME, DEVEPLOPER
from utils.tools import input_without
from utils.fileIO import get_csv_data, update_game_metadata, send_file, receive_file, update_game_metadata
import os
import time


def do_upload_game(client_socket):
    """
    Handles the upload process of a game from the client to the server.
    """
    try:
        # Step1. Check if the game file exists locally
        print("please place your file in the game directory and give it a clear naming like tic_tac_toe.py")
        game_name = input("Enter your file name (ignore .py) : ")
        file_path = f"{game_name}.py"
        if not os.path.isfile(file_path):
            print("File not found.")
            return

        # Step2. Gather game metadata
        intro = input_without('|', "Introduction of your game")
        metadata = f"UPLOAD|{game_name}|{intro}"
        client_socket.sendall(metadata.encode())

        # Step3. Wait for server response
        response = client_socket.recv(1024).decode()
        if response.startswith("OK"):
            # Proceed to upload the file
            _, uploader = response.split()
            send_file(client_socket, file_path)

            # Update local metadata
            update_game_metadata(game_name, intro, uploader)
            print(f"{game_name} uploaded successfully.")
            time.sleep(2)
        else:
            print(f"Upload rejected: {response}")

    except (ConnectionError, TimeoutError) as e:
        print(f"Upload failed due to network issue: {e}")


def handle_upload(data, client, addr, login_addr, game_list):
    """
    Handles the upload process from the client to the server.
    """
    try:
        # Step1. Parse metadata from client request
        _, info = data.split('|', maxsplit=1)
        game_name, intro = info.split('|')
        uploader = login_addr[addr]
        local_metadata = get_csv_data(LOCAL_GAME_META_FILE, key=GAME_NAME, value=game_name)

        # Step2. Send confirmation to proceed with file upload
        if local_metadata is None or local_metadata[DEVEPLOPER] == uploader: 
            client.sendall(f"OK {uploader}".encode())

        # Step3. Receive the game file and save it
        file_path = f"{game_name}.py"
        receive_file(client, file_path)

        # Step4. update game metadata
        if game_list is not None:
            game_list.append(game_name)
        update_game_metadata(game_name, intro, uploader)

    except Exception as e:
        print(f"Server encountered an error during upload: {e}")
        client.sendall(b"ERROR: Upload failed due to server error.")

