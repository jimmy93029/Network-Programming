import sys
import socket


def print_board(board):
    """Print the current state of the board."""
    for row in board:
        print(" | ".join(row))
        print("-" * 9)


def check_winner(board, player):
    """Check if the given player has won."""
    for i in range(3):
        if all([spot == player for spot in board[i]]):  
            return True
        if all([board[j][i] == player for j in range(3)]):  
            return True
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False


def is_draw(board):
    """Check if the game is a draw."""
    return all([spot != " " for row in board for spot in row])


def Tic_tac_toe(socket, player):
    """General game logic for Tic-Tac-Toe."""
    board = [[" " for _ in range(3)] for _ in range(3)]
    actions = ['1', '2', '3']
    current_player = "X"  # Player A starts with "X"
    print(f"Connected as Player {player}.")

    while True:
        print_board(board)

        if (current_player == "X" and player == "A") or (current_player == "O" and player == "B"):
            # Player's turn
            print("Your turn.")
            row = select_type("rows", actions) - 1
            col = select_type("cols", actions) - 1

            if row not in range(3) or col not in range(3) or board[row][col] != " ":
                print("Invalid move. Try again.")
                continue

            board[row][col] = current_player
            socket.send(f"{row},{col}".encode())
        else:
            # Opponent's turn
            print(f"Waiting for Player {'B' if player == 'A' else 'A'}'s move...")
            data = socket.recv(1024).decode()

            if not data:
                print("Connection lost or opponent has disconnected.")
                return False

            row, col = map(int, data.split(","))
            board[row][col] = current_player

        # Check for win or draw
        if check_winner(board, current_player):
            print_board(board)
            print(f"Player {current_player} wins!")
            return True

        if is_draw(board):
            print_board(board)
            print("It's a draw!")
            return True

        # Switch players
        current_player = "O" if current_player == "X" else "X"


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


def main():
    if len(sys.argv) < 3:
        print("Usage: python dark_chess.py <role> <socket_fd>")
        sys.exit(1)

    role = sys.argv[1]
    socket_fd = int(sys.argv[2])

    # Reconstruct the socket from the file descriptor
    game_socket = socket.fromfd(socket_fd, socket.AF_INET, socket.SOCK_STREAM)

    Tic_tac_toe(game_socket, role)


if __name__ == "__main__":
    main()
