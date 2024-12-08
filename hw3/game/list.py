import os
import json
import csv
from utils.variables import GAME_META_FILE, LOCAL_GAME_META_FILE
from utils.tools import format_table


def do_listing_my_game():
    """
    List all the games which the user maintains.
    """
    # Get the current directory and list files
    user_dir = os.getcwd()
    game_list = [file for file in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, file))]

    all_games = get_all_game_info(LOCAL_GAME_META_FILE)
    game_info = [game for game in all_games if game["GameName"] in game_list]

    # Display the game information
    display_game_info(game_info, title="My Game Table")


def do_listing_all_game(client_socket):
    """
    List all the games maintained in the lobby's external data source.
    """
    # Prepare the message
    command = "LIST"
    message = f"{command}"

    # Send the message to the server
    client_socket.sendall(message.encode())

    # Receive and process the server's response
    response = client_socket.recv(4096).decode()
    game_info = json.loads(response)  # Decode the JSON response from the server

    # Display the game information
    display_game_info(game_info, title="All Game Table")


def display_game_info(game_info, title):
    """
    Utility function to display game information in a formatted table using format_table.

    Args:
        game_info (list): A list of dictionaries containing game information.
        title (str): Title for the table.
    """
    # Define table structure
    header = ["Game Name", "Developer", "Introduction"]
    column_widths = [20, 15, 30]  # Adjust column widths as needed

    # If no game data, still show the table structure
    if not game_info:
        rows = []
        table = format_table(header, rows, column_widths, title=title, count=0)
    else:
        rows = [[game["GameName"], game["Developer"], game["Introduction"]] for game in game_info]
        table = format_table(header, rows, column_widths, title=title, count=len(game_info))

    print(table)


def get_all_game_info(file):
    """
    **(1-3). Save game file with an external data source:**
    Retrieves all game information from the external data source (e.g., `games.csv`)
    located in the lobby server's directory.

    This ensures that even if the server is restarted, the game metadata remains available.
    """
    game_info_list = []
    try:
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                game_info_list.append({
                    "GameName": row["GameName"],
                    "Developer": row["Developer"],
                    "Introduction": row["Introduction"]
                })
    except FileNotFoundError:
        print(f"Error: {file} not found.")
    return game_info_list


def handle_list_all_games(data, client, addr):
    """
    Handles the LIST_ALL_GAMES request from the client.
    """
    # Retrieve all game information
    all_games = get_all_game_info(GAME_META_FILE)

    # Send the game information back to the client
    client.sendall(json.dumps(all_games).encode())

