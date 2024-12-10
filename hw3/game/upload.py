from utils.variables import LOCAL_GAME_META_FILE, GAME_NAME, DEVEPLOPER, INTRO, VERSION
from utils.tools import input_without, get_csv_data, update_game_metadata
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
            update(game_name, intro, uploader)
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
        update(game_name, intro, uploader, game_list=game_list)

    except Exception as e:
        print(f"Server encountered an error during upload: {e}")
        client.sendall(b"ERROR: Upload failed due to server error.")


def update(game_name, intro, uploader, game_list=None):
    # update game list
    if game_list is not None:
        game_list.append(game_name)

    # update games.csv
    local_metadata = get_csv_data(LOCAL_GAME_META_FILE, key=GAME_NAME, value=game_name)
    version = int(local_metadata[VERSION]) + 1 if local_metadata else 1
    updated_metadata = {
        GAME_NAME: game_name,
        INTRO: intro,
        DEVEPLOPER: uploader, 
        VERSION: version,
    }
    update_game_metadata(updated_metadata, LOCAL_GAME_META_FILE)


def send_file(client_socket, file_path):
    """
    Sends a file from the specified file path.
    """
    try:
        with open(file_path, 'rb') as f:
            total_bytes_sent = 0
            while chunk := f.read(1024):
                client_socket.sendall(chunk)
                total_bytes_sent += len(chunk)
                print(f"Sent {total_bytes_sent} bytes so far...")
        client_socket.sendall(b"FILE_TRANSFER_COMPLETE")
        time.sleep(3)
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")


def receive_file(client_socket, file_path):
    """
    Receives a file and writes it to the specified file path.
    """
    total_bytes_received = 0
    with open(file_path, 'wb') as f:
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:  # Connection closed unexpectedly
                print("Connection closed unexpectedly.")
                break
            
            # Check if the termination marker is in the chunk
            if b"FILE_TRANSFER_COMPLETE" in chunk:
                chunk, _ = chunk.split(b"FILE_TRANSFER_COMPLETE", 1)
                f.write(chunk)  # Write the remaining data in the chunk
                total_bytes_received += len(chunk)
                print("File transfer complete.")
                break

            # Write the received chunk to the file
            f.write(chunk)
            total_bytes_received += len(chunk)
            print(f"Total bytes received: {total_bytes_received}")

    print(f"File received and saved to {file_path}.")


