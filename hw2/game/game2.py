import socket
from rules import init_chinese_chess_board, print_chinese_chess_board, is_valid_move_chinese_chess


# Check if the game has a winner by verifying if the generals are still on the board
def check_victory(board):
    red_general_alive = any("帥" in row for row in board)
    black_general_alive = any("將" in row for row in board)
    
    if not red_general_alive:
        print("Player B wins! The Red General has been captured.")
        return "B"
    elif not black_general_alive:
        print("Player A wins! The Black General has been captured.")
        return "A"
    return None


def Chinese_chess(Me, socket):
    board = init_chinese_chess_board()
    current_player = Me
    opponent = "A" if Me == "B" else "B" 

    while True:
        print_chinese_chess_board(board)

        # Check for victory condition after each move
        winner = check_victory(board)
        if winner:
            print(f"Game Over. Player {winner} wins!")
            break

        if current_player == Me:
            print(f"Player {Me}, please enter your move (e.g., '0 1 1 1' means moving from (0,1) to (1,1)):")
            move = input("Enter your move: ")
            start_row, start_col, end_row, end_col = map(int, move.split())
            
            # Validate move
            if not is_valid_move_chinese_chess(board, start_row, start_col, end_row, end_col, current_player):
                print("Invalid move. Please try again.")
                continue

            # Update board and send move to opponent
            board[end_row][end_col] = board[start_row][start_col]
            board[start_row][start_col] = " "
            socket.send(move.encode())
        else:
            # Receive move from opponent
            print(f"Waiting for Player {opponent}'s move...")
            move = socket.recv(1024).decode()
            start_row, start_col, end_row, end_col = map(int, move.split())
            board[end_row][end_col] = board[start_row][start_col]
            board[start_row][start_col] = " "

        # Switch turns
        current_player = opponent if current_player == Me else Me



