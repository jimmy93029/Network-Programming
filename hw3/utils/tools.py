import csv
from utils.variables import GAME_NAME, INTRO, DEVEPLOPER, VERSION


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
