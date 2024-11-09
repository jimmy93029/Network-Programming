

def select_type(choice_name, choice_list, choice="0"): 

    while not choice.isdigit() or int(choice) not in [1, 2]:
        choice = input(f"Which {choice_name} do you want? \n\
                        (1) {choice_list[0]} \n\
                        (2) {choice_list[1]} \n\
                        Please input your choose : ")

        if not choice.isdigit():
            print(f"Please input {choice_name} as a digit.")
        elif int(choice) not in [1, 2]:
            print(f"Please input {choice_name} as a number from {{1, 2}}.")

    return int(choice)