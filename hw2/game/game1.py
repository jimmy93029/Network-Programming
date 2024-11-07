

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
    current_player = "X"  # Player A starts with "X"
    print(f"Connected as Player {player}.")

    while True:
        print_board(board)

        if (current_player == "X" and player == "A") or (current_player == "O" and player == "B"):
            # Player's turn
            print("Your turn.")
            row = int(input("Enter row (1-3): ")) - 1
            col = int(input("Enter column (1-3): ")) - 1

            if row not in range(3) or col not in range(3) or board[row][col] != " ":
                print("Invalid move. Try again.")
                continue

            board[row][col] = current_player
            socket.send(f"{row},{col}".encode())
        else:
            # Opponent's turn
            print(f"Waiting for Player {'B' if player == 'A' else 'A'}'s move...")
            data = socket.recv(1024).decode()
            row, col = map(int, data.split(","))
            board[row][col] = current_player

        # Check for win or draw
        if check_winner(board, current_player):
            print_board(board)
            print(f"Player {current_player} wins!")
            break

        if is_draw(board):
            print_board(board)
            print("It's a draw!")
            break

        # Switch players
        current_player = "O" if current_player == "X" else "X"

    socket.close()
