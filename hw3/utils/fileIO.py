import csv
from utils.variables import GAME_NAME, INTRO, DEVEPLOPER, VERSION
import time


def get_csv_data(csv_file, key=None, value=None):
    """
    Fetches the entire content of a CSV file as a list of dictionaries,
    or retrieves a specific record based on a key-value pair.
    """
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            
            if key and value:
                for row in data:
                    if row.get(key) == value:
                        return row  # Return the first matching record
                return None  # Return None if no match is found
            
            return data  # Return the entire content if no key-value is specified
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file}")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None


def update_csv_file(new_row, csv_file, key_column, fieldnames):
    """
    Updates or appends a row to a CSV file.
    """
    rows = []
    key_value = new_row.get(key_column)
    updated = False

    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get(key_column) == key_value:
                    rows.append(new_row)  # Replace the existing row
                    updated = True
                else:
                    rows.append(row)
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file}. Creating a new file.")

    if not updated:
        rows.append(new_row)  # Append new row if not found

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_game_metadata(new_game, csv_file):
    """
    Updates or appends game metadata in the CSV file.
    """
    fieldnames = [GAME_NAME, INTRO, DEVEPLOPER, VERSION]
    update_csv_file(new_game, csv_file, GAME_NAME, fieldnames)


def update_user_data(new_user, csv_file):
    """
    Updates or appends user data in the CSV file.
    """
    fieldnames = ["username", "password"]
    update_csv_file(new_user, csv_file, "username", fieldnames)


def send_file(client_socket, file_path):
    """
    Sends a file from the specified file path.
    """
    try:
        time.sleep(2)
        with open(file_path, 'rb') as f:
            total_bytes_sent = 0
            while chunk := f.read(1024):
                client_socket.sendall(chunk)
                total_bytes_sent += len(chunk)
                print(f"Sent {total_bytes_sent} bytes so far...")
        client_socket.sendall(b"FILE_TRANSFER_COMPLETE")
        time.sleep(2)
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")


def receive_file(client_socket, file_path):
    """
    Receives a file and writes it to the specified file path.
    """
    total_bytes_received = 0
    print(f"Total bytes received: {total_bytes_received}")
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
    time.sleep(2)