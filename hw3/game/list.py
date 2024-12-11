import json
from utils.variables import LOCAL_GAME_META_FILE, GAME_NAME, DEVEPLOPER, INTRO
from utils.tools import format_table
from utils.fileIO import get_csv_data


def do_listing_my_game():
    """
    List all the games which the user maintains.
    """
    # Get the current directory and list files
    my_games = get_csv_data(LOCAL_GAME_META_FILE)

    # Display the game information
    display_game_info(my_games, title="My Game Table")


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
    """
    # Define table structure
    header = ["Game Name", "Developer", "Introduction"]
    column_widths = [20, 15, 30]  # Adjust column widths as needed

    # If no game data, still show the table structure
    if not game_info:
        rows = []
        table = format_table(header, rows, column_widths, title=title, count=0)
    else:
        rows = [[game[GAME_NAME], game[DEVEPLOPER], game[INTRO]] for game in game_info]
        table = format_table(header, rows, column_widths, title=title, count=len(game_info))

    print(table)


def handle_list_all_games(data, client, addr):
    """
    Handles the LIST_ALL_GAMES request from the client.
    """
    # Retrieve all game information
    all_games = get_csv_data(LOCAL_GAME_META_FILE)

    # Send the game information back to the client
    client.sendall(json.dumps(all_games).encode())

