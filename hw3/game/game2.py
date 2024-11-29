from utils.tools import select_type
from .rules import init_chinese_chess_board, print_chinese_chess_board, flip_piece, is_valid_move_dark_chess, get_board, colored_piece


def check_victory(board, hidden_board):
    """Check if either side has no pieces left, indicating a victory for the other side."""
    red_pieces = any(piece in "帥仕相車馬砲兵" for row in board for piece in row) + \
                    any(piece in "帥仕相車馬砲兵" for row in hidden_board for piece in row)
    black_pieces = any(piece in "将士象车马炮卒" for row in board for piece in row) + \
                   any(piece in "将士象车马炮卒" for row in hidden_board for piece in row)
    if not red_pieces:
        return "B"  # Black wins
    elif not black_pieces:
        return "A"  # Red wins
    return None  # No victory


def check_draw(move_count, last_capture_move):
    """Check if the game is a draw due to no captures in the last 50 moves."""
    if move_count - last_capture_move >= 50:
        return True
    return False


def dark_chess(socket, Me):
    """Main game function to play dark chess using a socket connection."""

    board, hidden_board = get_board(socket, Me)
    current_player = "A"
    opponent = "A" if Me == "B" else "B"
    move_count = 0  # Count total moves
    last_capture_move = 0  # Track last move when a piece was captured
    actions = ["flip", "move", "surrender"]

    while True:
        print_chinese_chess_board(board)

        # Check for victory condition after each move
        winner = check_victory(board, hidden_board)
        if winner:
            print(f"Game Over. Player {winner} wins!")
            return True

        # Check for draw condition
        if check_draw(move_count, last_capture_move):
            print("Game ends in a draw due to no captures in the last 50 moves.")
            return True

        if current_player == Me:
            # Player's turn: choose between flipping or moving
            idx = select_type(f"Choose action for {colored_piece(Me)}", actions)
            action = actions[idx-1]

            if action == "flip":
                try:
                    row, col = map(int, input("Enter row and column to flip (e.g., '1 2'): ").split())
                    if not flip_piece(board, hidden_board, row, col):
                        print("Invalid flip. Please try again.")
                        continue
                    socket.send(f"flip {row} {col}".encode())
                except ValueError:
                    print("Invalid input. Please enter two integers separated by space.")
                    continue

            elif action == "move":
                try:
                    move = input("Enter your move (e.g., '0 1 1 1' for moving from (0,1) to (1,1)): ")
                    start_row, start_col, end_row, end_col = map(int, move.split())

                    # Validate move
                    if not is_valid_move_dark_chess(board, start_row, start_col, end_row, end_col, current_player):
                        print("Invalid move. Please try again.")
                        continue

                    # Execute the move
                    if board[end_row][end_col] != " ":
                        last_capture_move = move_count  # Reset capture count if capturing a piece
                    board[end_row][end_col] = board[start_row][start_col]
                    board[start_row][start_col] = " "
                    socket.send(f"move {move}".encode())
                except ValueError:
                    print("Invalid input. Please enter four integers separated by spaces.")
                    continue
            elif action == "surrender":
                socket.send(f"surrender {Me}".encode())
                print(f"Game Over. Player {opponent} wins!")
                break     

        else:
            # Opponent's turn: wait for their action
            print(f"Waiting for Player {colored_piece(opponent)}'s action...")
            data = socket.recv(1024).decode()

            if not data:
                print("Connection lost or opponent has disconnected.")
                return False
            action, *params = data.split()
            
            if action == "flip":
                row, col = map(int, params)
                flip_piece(board, hidden_board, row, col)
            elif action == "move":
                start_row, start_col, end_row, end_col = map(int, params)
                if board[end_row][end_col] != " ":
                    last_capture_move = move_count  # Reset capture count for opponent's capture
                board[end_row][end_col] = board[start_row][start_col]
                board[start_row][start_col] = " "
            elif action == "surrender":
                print(f"Game Over. Player {Me} wins!")
                return True      

        move_count += 1  # Increment move count
        current_player = opponent if current_player == Me else Me
