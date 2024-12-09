from utils.variables import LOCAL_GAME_META_FILE
import os
import csv


def do_upload_game(client_socket, game_name):
    """
    Handles the upload process of a game from the client to the server.
    """
    try:
        # Check if the game file exists locally
        file_path = f".{game_name}.py"
        if not os.path.isfile(file_path):
            print("File not found.")
            return

        # Gather game metadata
        description = input("Enter the description of your game: ")
        metadata = f"UPLOAD {game_name} {description}"
        client_socket.sendall(metadata.encode())

        # Wait for server response
        response = client_socket.recv(1024).decode()
        if response.startswith("OK"):
            # Proceed to upload the file
            _, uploader = response.split()
            send_file(client_socket, file_path)

            # Update local metadata
            update(game_name, description, file_path, uploader)
            print(f"{game_name} uploaded successfully.")
        else:
            print(f"Upload rejected: {response}")

    except (ConnectionError, TimeoutError) as e:
        print(f"Upload failed due to network issue: {e}")


def handle_upload(data, client, addr, login_addr):
    """
    Handles the upload process from the client to the server.
    """
    try:
        # Parse metadata from client request
        _, game_name, description = data.split(' ')
        uploader = login_addr[addr]

        # Send confirmation to proceed with file upload
        client.sendall(f"OK {uploader}".encode())

        # Receive the game file and save it
        file_path = f".{game_name}.py"
        receive_file(client, file_path)

        # Simplified logic to update game metadata
        update(game_name, description, file_path, uploader)

    except Exception as e:
        print(f"Server encountered an error during upload: {e}")
        client.sendall(b"ERROR: Upload failed due to server error.")


def update(game_name, description, file_path, uploader):
    local_metadata = get_game_metadata(game_name, LOCAL_GAME_META_FILE)
    version = int(local_metadata['version']) + 1 if local_metadata else 1
    updated_metadata = {
        'game_name': game_name,
        'description': description,
        'author': uploader, 
        'version': version,
        'filepath': file_path
    }
    update_game_metadata(updated_metadata, LOCAL_GAME_META_FILE)


def receive_file(client_socket, file_path):
    """
    Receives a file and writes it to the specified file path.
    """
    with open(file_path, 'wb') as f:
        while chunk := client_socket.recv(1024):
            f.write(chunk)
    print(f"File received and saved to {file_path}.")


def send_file(client_socket, file_path):
    """
    Sends a file from the specified file path.
    """
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024):
                client_socket.sendall(chunk)
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")


def get_game_metadata(game_name, metadata_file):
    """
    Retrieves game metadata from a specified metadata file.
    """
    try:
        with open(metadata_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['game_name'] == game_name:
                    return row
    except FileNotFoundError:
        print(f"Metadata file not found: {metadata_file}")
    return None


def update_game_metadata(game_metadata, metadata_file):
    """
    Updates the metadata file with the latest game metadata.
    """
    rows = []
    try:
        with open(metadata_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['game_name'] != game_metadata['game_name']:
                    rows.append(row)
    except FileNotFoundError:
        print(f"Creating new metadata file: {metadata_file}")

    # Add updated metadata
    rows.append(game_metadata)
    with open(metadata_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['game_name', 'description', 'author', 'version', 'filepath'])
        writer.writeheader()
        writer.writerows(rows)

