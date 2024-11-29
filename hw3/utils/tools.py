

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