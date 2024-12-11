import csv
import os
from utils.variables import GAME_NAME, INTRO, DEVEPLOPER, VERSION, LOCAL_GAME_META_FILE, USER_DATA, STATUS, IDLE, SOCKET, ADDRESS
from utils.fileIO import get_csv_data


def select_type(choice_name, choice_list, choice="0"): 
    # Create a list of valid choices based on the length of choice_list
    valid_choices = list(range(1, len(choice_list) + 1))

    # Generate the options dynamically based on choice_list
    options_text = "\n".join(f"({i}) {choice}" for i, choice in enumerate(choice_list, 1))

    while not choice.isdigit() or int(choice) not in valid_choices:
        choice = input(f"Which {choice_name} do you want? \n{options_text}\nPlease input your choice: ")

        if not choice.isdigit():
            print(f"Please input {choice_name} as a digit.\n")
        elif int(choice) not in valid_choices:
            print(f"Please input {choice_name} as a number from {valid_choices}\n")

    return int(choice)


def format_table(header, rows, column_widths, title=None, count=None):
    """
    Formats data into a table string with a header, rows, and optional title/count.
    """
    table = []

    table.append("-" * (sum(column_widths) + len(column_widths) - 1))
    # Add title and count if provided
    if title and count is not None:
        table.append(f"{title} 數量: {count}")

    # Add the separator line
    table.append("-" * (sum(column_widths) + len(column_widths) - 1))

    # Add the header
    table.append(" | ".join(f"{header[i]:<{column_widths[i]}}" for i in range(len(header))))
    table.append("-" * (sum(column_widths) + len(column_widths) - 1))

    # Add the rows
    for row in rows:
        table.append(" | ".join(f"{row[i]:<{column_widths[i]}}" for i in range(len(row))))
    table.append("-" * (sum(column_widths) + len(column_widths) - 1))

    return "\n".join(table)


def input_without(sign, prompt):
    answer = None
    while True:
        answer = input(f"{prompt} (don't input '{sign}' ): ")
        if sign not in answer:
            break
        else:
            print(f"I have said that don't input sign {sign} ")
    return answer


def server_init(game_list):
    """
    Initializes server data and loads game metadata into the game_list.
    """
    # Ensure the metadata file exists
    if not os.path.exists(LOCAL_GAME_META_FILE):
        with open(LOCAL_GAME_META_FILE, 'w') as f:
            # Initialize with a header if the file is created
            writer = csv.DictWriter(f, fieldnames=[GAME_NAME, INTRO, DEVEPLOPER, VERSION])
            writer.writeheader()

    # Ensure the user data file exists
    if not os.path.exists(USER_DATA):
        with open(USER_DATA, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=["username", "password"])
            writer.writeheader()

    # Fetch all game data from the metadata file
    game_data = get_csv_data(LOCAL_GAME_META_FILE)
    if game_data:
        # Extract game names and populate the game_list
        game_list.extend(row[GAME_NAME] for row in game_data if GAME_NAME in row)
    else:
        print("No games found in metadata.")


def client_init():
    if not os.path.exists(LOCAL_GAME_META_FILE):
        with open(LOCAL_GAME_META_FILE, 'w') as f:
            # Initialize with a header if the file is created
            writer = csv.DictWriter(f, fieldnames=[GAME_NAME, INTRO, DEVEPLOPER, VERSION])
            writer.writeheader()


def user_init(username, online_users, client, mailbox, invitations, addr):
    online_users[username] = {STATUS: IDLE, SOCKET: client, ADDRESS:addr}
    mailbox[username] = []
    invitations[username] = {}