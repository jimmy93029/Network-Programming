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

def PlayerA_Game1(PlayerA_socket):
    """Game logic for Player A (host)."""
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"  # Player A uses "X"
    
    while True:
        print_board(board)
        if current_player == "X":
            print("Your turn.")
            row = int(input("Enter row (1-3): ")) - 1
            col = int(input("Enter column (1-3): ")) - 1

            if row not in range(3) or col not in range(3) or board[row][col] != " ":
                print("Invalid move. Try again.")
                continue

            board[row][col] = current_player
            PlayerA_socket.send(f"{row},{col}".encode())
        else:
            print("Waiting for Player B's move...")
            data = PlayerA_socket.recv(1024).decode()
            row, col = map(int, data.split(","))
            board[row][col] = current_player

        if check_winner(board, current_player):
            print_board(board)
            print(f"Player {current_player} wins!")
            break

        if is_draw(board):
            print_board(board)
            print("It's a draw!")
            break

        current_player = "O" if current_player == "X" else "X"

    PlayerA_socket.close()

def PlayerB_Game1(PlayerB_socket):
    """Game logic for Player B (client)."""
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"  # Player A uses "X"
    print("Connected to Player A.")

    while True:
        print_board(board)
        
        if current_player == "O":
            print("Your turn.")
            row = int(input("Enter row (1-3): ")) - 1
            col = int(input("Enter column (1-3): ")) - 1

            if row not in range(3) or col not in range(3) or board[row][col] != " ":
                print("Invalid move. Try again.")
                continue

            board[row][col] = current_player
            PlayerB_socket.send(f"{row},{col}".encode())
        else:
            print("Waiting for Player A's move...")
            data = PlayerB_socket.recv(1024).decode()
            row, col = map(int, data.split(","))
            board[row][col] = current_player

        if check_winner(board, current_player):
            print_board(board)
            print(f"Player {current_player} wins!")
            break

        if is_draw(board):
            print_board(board)
            print("It's a draw!")
            break

        current_player = "O" if current_player == "X" else "X"

    PlayerB_socket.close()
