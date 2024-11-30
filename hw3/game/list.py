import os
import json
import csv
from utils.variables import GAME_META_FILE


def do_list_my_game(client_socket):
    """
    **(1-1). List all the games which you maintain yourself:**
    Allows users to view their own published games and their details
    (e.g., publisher, game description, etc.).

    This function gathers the file names in the user's current directory
    and queries the server for metadata about matching games.
    """
    # Get the current directory and list files
    user_dir = os.getcwd()
    game_list = [file for _, _, files in os.walk(user_dir) for file in files]

    # Prepare the message in "COMMAND DATA" format
    command = "LIST_MY_GAMES"
    data = json.dumps(game_list)  # Convert game list to JSON string for transmission
    message = f"{command} {data}"  # Combine command and data into a single string

    # Send the message to the server
    client_socket.sendall(message.encode())

    # Receive and process the server's response
    response = client_socket.recv(4096).decode()
    game_info = json.loads(response)  # Decode the JSON response from the server

    # Display the game information in a formatted table
    display_game_info(game_info)


def list_all_game(client_socket):
    """
    **(1-1). List all the games:**
    This function sends a request to the server to retrieve all games
    maintained in the lobby's external data source (e.g., CSV file).
    """
    # Prepare the message in "COMMAND DATA" format
    command = "LIST_ALL_GAMES"
    message = f"{command}"  # No additional data required

    # Send the message to the server
    client_socket.sendall(message.encode())

    # Receive and process the server's response
    response = client_socket.recv(4096).decode()
    game_info = json.loads(response)  # Decode the JSON response from the server

    # Display the game information in a formatted table
    display_game_info(game_info)


def display_game_info(game_info):
    """
    Utility function to display game information in a formatted table.
    """
    print("\n" + "=" * 60)
    print(f"{'Game Name':<20} | {'Developer':<10} | {'Introduction'}")
    print("=" * 60)
    for game in game_info:
        print(f"{game['GameName']:<20} | {game['Developer']:<10} | {game['Introduction']}")
    print("=" * 60)


def get_all_game_info():
    """
    **(1-3). Save game file with an external data source:**
    Retrieves all game information from the external data source (e.g., `games.csv`)
    located in the lobby server's directory.

    This ensures that even if the server is restarted, the game metadata remains available.
    """
    game_info_list = []
    try:
        with open(GAME_META_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                game_info_list.append({
                    "GameName": row["GameName"],
                    "Developer": row["Developer"],
                    "Introduction": row["Introduction"]
                })
    except FileNotFoundError:
        print(f"Error: {GAME_META_FILE} not found.")
    return game_info_list


def handle_list_my_games(data, client, addr):
    """
    **(1-1). List all the games which you maintain yourself:**
    Handles the LIST_MY_GAMES request from the client. It filters games
    in the lobby database (`games.csv`) based on the file names in the user's current directory.
    """
    # Extract the command and data from the message
    _, data = data.split(" ", 1)  # Split into command and data
    game_list = json.loads(data)  # Parse the JSON data

    # Query the CSV database for each game in the current directory
    all_games = get_all_game_info()
    game_info_list = [game for game in all_games if game["GameName"] in game_list]

    # Send the game information back to the client
    client.sendall(json.dumps(game_info_list).encode())


def handle_list_all_games(client, addr):
    """
    **(1-1). List all the games:**
    Handles the LIST_ALL_GAMES request from the client. It sends all
    game information from the lobby's external data source (`games.csv`)
    to the client without filtering.
    """
    # Retrieve all game information
    all_games = get_all_game_info()

    # Send the game information back to the client
    client.sendall(json.dumps(all_games).encode())
