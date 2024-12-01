from utils.connection import connect_to_server
from utils.variables import USER_DATA
import csv
import os


""" Client """
def do_register():
    try:
        client_socket = connect_to_server()

        username = input("Enter a username for registration: ")
        password = input("Enter a password for registration: ")

        # The player enters a username and a password.
        message = f"REGISTER {username} {password}"
        client_socket.sendall(message.encode())
        
        response = client_socket.recv(1024).decode()
        print("Server response:", response)

        client_socket.close()

    except (ConnectionError, TimeoutError) as e:
        print(f"Register failed due to network issue: {e}")


"""Client"""
def handle_register(data, client, addr):
    """
    Handles user registration.
    """
    _, username, password = data.split()
    user_db = load_user_db()

    # The server verifies whether the username already exists
    if username in user_db:
        message = "Username already exists.\nPlease enter another username for registration."
        print(message)
        client.sendall(message.encode())
    else:
        # If the username does not exist, the server stores the username and password
        user_db[username] = password
        save_user_db(user_db)  # Save updated user_db to file
        message = "Registration successful"
        print(message)
        client.sendall(message.encode())


def load_user_db():
    """
    Load user data from a CSV file into a dictionary.
    """
    user_db = {}
    if os.path.exists(USER_DATA):
        with open(USER_DATA, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:  # Ensure each row has username and password
                    username, password = row
                    user_db[username] = password
    return user_db

def save_user_db(user_db):
    """
    Save user data from a dictionary to a CSV file.
    """
    with open(USER_DATA, "w", newline="") as file:
        writer = csv.writer(file)
        for username, password in user_db.items():
            writer.writerow([username, password])


