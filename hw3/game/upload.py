from utils.variables import SERVER_FOLDER, GAME_META_FILE
import csv
import time
import os


def do_upload_game(client_socket, file_path):
    """
    Handles the upload process of a game to the server.
    """
    try:
        # Send upload request with metadata
        game_name = input("Enter you file name (ignore .py) : ")
        if not os.path.isfile(file_path):
            print("file not found")
            return
        
        description = input("Introduction of your game : ")
        metadata = f"UPLOAD {game_name} {description}"
        client_socket.sendall(metadata.encode())

        # Wait for server response
        response = client_socket.recv(1024).decode()
        file_path = os.path.join(os.getcwd(), game_name + ".py")

        if response.startswith("OK"):
            # Proceed to upload the file
            time.sleep(2)
            with open(file_path, 'rb') as f:
                while chunk := f.read(1024):
                    client_socket.sendall(chunk)
            print(f"{game_name} uploaded successfully.")
        else:
            print("Upload rejected:", response)

    except (ConnectionError, TimeoutError) as e:
        print(f"Upload failed due to network issue: {e}")



def handle_upload(data, client, addr, login_addr, online_users):
    """
    Handles the upload process from the client.
    """
    try:
        # Parse metadata from client request
        _, game_name, description = data.split(' ')
        username = login_addr[addr]

        # Check if the user is the creator of the game
        game_metadata = get_game_metadata(game_name)
        if game_metadata and game_metadata['author'] != username:
            client.sendall(f"ERROR: Only the creator {game_metadata['author']} can update this game.".encode())
            return
        
        # Send confirmation to proceed with file upload
        client.sendall("OK: Ready to receive the game file.".encode())
        
        # Receive the game file and save it
        server_path = os.path.join(SERVER_FOLDER, f"{game_name}.py")
        with open(server_path, 'wb') as f:
            while chunk := client.recv(1024):
                f.write(chunk)

        # Update game metadata
        if game_metadata:
            new_version = int(game_metadata['version']) + 1
            game_metadata.update({
                'description': description,
                'version': new_version,
                'filepath': server_path
            })
        else:
            game_metadata = {
                'game_name': game_name,
                'author': username,
                'description': description,
                'version': 1,
                'filepath': server_path
            }

        update_game_metadata(game_metadata)
        client.sendall(f"Upload successful: {game_name}, version {game_metadata['version']}".encode())

    except Exception as e:
        print(f"Server encountered an error during upload: {e}")
        client.sendall("ERROR: Upload failed due to server error.".encode())


def get_game_metadata(game_name):
    """
    Retrieves game metadata from the CSV file.
    """
    try:
        with open(GAME_META_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['game_name'] == game_name:
                    return row
    except FileNotFoundError:
        return None
    return None


def update_game_metadata(game_metadata):
    """
    Updates the game metadata in the CSV file.
    """
    rows = []
    try:
        with open(GAME_META_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['game_name'] != game_metadata['game_name']:
                    rows.append(row)
    except FileNotFoundError:
        pass  # If the file doesn't exist, we'll create it.

    rows.append(game_metadata)
    with open(GAME_META_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['game_name', 'description', 'author', 'version', 'filepath'])
        writer.writeheader()
        writer.writerows(rows)