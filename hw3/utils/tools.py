

def select_type(choice_name, choice_list, choice="0"): 
    # Create a list of valid choices based on the length of choice_list
    valid_choices = list(range(1, len(choice_list) + 1))

    # Generate the options dynamically based on choice_list
    options_text = "\n".join(f"({i}) {choice}" for i, choice in enumerate(choice_list, 1))

    while not choice.isdigit() or int(choice) not in valid_choices:
        choice = input(f"Which {choice_name} do you want? \n{options_text}\nPlease input your choice: ")

        if not choice.isdigit():
            print(f"Please input {choice_name} as a digit.")
        elif int(choice) not in valid_choices:
            print(f"Please input {choice_name} as a number from {valid_choices}.")

    return int(choice)


def format_table(header, rows, column_widths, title=None, count=None):
    """
    Formats data into a table string with a header, rows, and optional title/count.

    Args:
        header (list): A list of column headers.
        rows (list): A list of rows, where each row is a list of strings.
        column_widths (list): A list of integers specifying column widths.
        title (str): An optional title for the table.
        count (int): An optional count to display in the title.

    Returns:
        str: The formatted table as a string.
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


