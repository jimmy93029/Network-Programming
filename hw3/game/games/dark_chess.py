from utils.tools import select_type
import sys 
import socket


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


def main():
    role = sys.argv[1]
    socket_fd = int(sys.argv[2])  # File descriptor for the socket

    # Wrap the file descriptor as a socket
    game_socket = socket.fromfd(socket_fd, socket.AF_INET, socket.SOCK_STREAM)
    dark_chess(game_socket, role)


if __name__ == "__main__":
    main()



# --------------------------------------- rules ------------------------------------------------

import random

# Define colors for displaying red and blue pieces
RED = "\033[31m"
BLUE = "\033[34m"
RESET = "\033[0m"

red_pieces = "帥仕相車馬砲兵A"
blue_pieces = "將士象车马炮卒B"

def init_chinese_chess_board():
    """Initialize the board with shuffled pieces and hidden pieces represented by '*'."""
    pieces = [
        "帥", "仕", "仕", "相", "相", "車", "車", "馬", "馬", "砲", "砲", "兵", "兵", "兵", "兵", "兵",
        "將", "士", "士", "象", "象", "车", "车", "马", "马", "炮", "炮", "卒", "卒", "卒", "卒", "卒"
    ]
    random.shuffle(pieces)
    board = [["*" for _ in range(8)] for _ in range(4)]
    hidden_board = [pieces[i*8:(i+1)*8] for i in range(4)]
    return board, hidden_board


def get_board(socket, Me):
    if Me == "A":
        board, hidden_board = init_chinese_chess_board()
        board_data = "".join("".join(row) for row in hidden_board)
        socket.send(board_data.encode())  # Send encoded hidden_board as a single string
    else:
        board = [["*" for _ in range(8)] for _ in range(4)]
        board_data = socket.recv(2048).decode()  # Increase buffer size if necessary
        hidden_board = [list(board_data[i*8:(i+1)*8]) for i in range(4)]  # Ensure nested list

    return board, hidden_board


def colored_piece(piece):
    """Return the piece with color coding based on its team."""
    
    if piece in red_pieces:
        return RED + piece + RESET
    elif piece in blue_pieces:
        return BLUE + piece + RESET
    else:
        return piece


def print_chinese_chess_board(board):
    """Display the board with improved alignment for row and column indicators."""
    # Print column headers
    col_header = "   " + "  ".join(map(str, range(8)))
    print(col_header)
    print("  +" + "---+" * 8)

    # Print each row with row index
    for i, row in enumerate(board):
        # Use colored_piece function to color each piece in the row
        formatted_row = f"{i} | " + " | ".join(colored_piece(piece) for piece in row) + " |"
        print(formatted_row)
        print("  +" + "---+" * 8)


def flip_piece(board, hidden_board, row, col):
    """Flip a piece on the board, revealing its hidden identity."""
    if board[row][col] != "*":
        print("Piece is already flipped!")
        return False
    board[row][col] = hidden_board[row][col]  # Reveal the actual piece
    hidden_board[row][col] = " "  # Update the hidden board to mark as flipped
    return True


def is_valid_move_dark_chess(board, start_row, start_col, end_row, end_col, player):
    """Check if a move is valid for dark chess, including flipping or moving/eating."""
    piece = board[start_row][start_col]
    target = board[end_row][end_col]

    # If piece is hidden or empty, movement is invalid
    if piece == "*" or piece == " ":
        print("No piece to move.")
        return False

    # Ensure players only move their own pieces
    if player == "A" and piece not in red_pieces:
        return False
    if player == "B" and piece not in blue_pieces:
        return False

    # For non-cannon pieces, only one-step moves are allowed
    if piece not in "砲炮":
        if abs(start_row - end_row) + abs(start_col - end_col) != 1:
            print("Pieces can only move one step horizontally or vertically.")
            return False
    elif piece in "砲炮":
        # Cannon can jump over exactly one piece to capture
        if not is_valid_cannon_move(board, start_row, start_col, end_row, end_col):
            return False

    # Check capture rules
    if target != " ":
        if player == "A" and target in red_pieces:
            print("You can't eat your own piece.")
            return False
        if player == "B" and target in blue_pieces:
            print("You can't eat your own piece.")
            return False
        if not is_valid_eat(piece, target):
            print("This piece cannot eat the target piece based on the rules.")
            return False

    return True


def is_valid_eat(attacker, defender):
    """Determine if the attacker can eat the defender based on dark chess rules."""
    hierarchy = {
        "帥": ["將", "士", "象", "车", "马", "炮"],
        "將": ["帥", "仕", "相", "車", "馬", "砲"],
        "仕": ["士", "象", "车", "马", "炮", "卒"],
        "士": ["仕", "相", "車", "馬", "砲", "兵"],
        "相": ["象", "车", "马", "炮", "卒"],
        "象": ["相", "車", "馬", "砲", "兵"],
        "車": ["车", "象", "车", "马", "炮", "卒"],
        "车": ["車", "馬", "砲", "兵"],
        "馬": ["马", "炮", "卒"],
        "马": ["馬", "砲", "兵"],
        "砲": ["將", "士", "象", "车", "马", "炮", "卒"],
        "炮": ["帥", "仕", "相", "車", "馬", "砲", "兵"],
        "兵": ["卒", "將"],
        "卒": ["兵", "帥"]
    }
    return defender in hierarchy.get(attacker, [])


def is_valid_cannon_move(board, start_row, start_col, end_row, end_col):
    """Check if cannon can move to a position by jumping exactly one piece when capturing."""
    if start_row != end_row and start_col != end_col:
        return False
    count_between = 0
    if start_row == end_row:
        step = 1 if start_col < end_col else -1
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] != " ":
                count_between += 1
    else:
        step = 1 if start_row < end_row else -1
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] != " ":
                count_between += 1
    if board[end_row][end_col] == " ":
        return count_between == 0
    else:
        return count_between == 1
