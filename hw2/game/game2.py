import random

def init_chinese_chess_board():
    """Initialize the board with shuffled pieces and hidden pieces represented by '*'."""
    pieces = [
        "帥", "仕", "仕", "相", "相", "車", "車", "馬", "馬", "砲", "砲", "兵", "兵", "兵", "兵", "兵",
        "將", "士", "士", "象", "象", "车", "车", "马", "马", "炮", "炮", "卒", "卒", "卒", "卒", "卒"
    ]
    random.shuffle(pieces)
    # Replace all pieces with '*' to indicate they are face-down
    board = [["*" for _ in range(8)] for _ in range(4)]
    hidden_board = [pieces[i*8:(i+1)*8] for i in range(4)]
    return board, hidden_board

def print_chinese_chess_board(board):
    """Display the board with flipped pieces."""
    print("  0 1 2 3 4 5 6 7")   # Column indices
    for i, row in enumerate(board):
        print(f"{i} " + " ".join(row))

def flip_piece(board, hidden_board, row, col):
    """Flip a piece on the board."""
    if board[row][col] != "*":
        print("Piece is already flipped!")
        return False
    # Replace '*' with the actual piece from the hidden board
    board[row][col] = hidden_board[row][col]
    return True


def check_victory(board):
    """Check if either side has no pieces left."""
    red_pieces = any(piece in "帥仕相車馬砲兵" for row in board for piece in row)
    black_pieces = any(piece in "将士象车马炮卒" for row in board for piece in row)
    if not red_pieces:
        return "B"
    elif not black_pieces:
        return "A"
    return None


def dark_chess(socket, Me):
    """Play dark chess game."""
    board, hidden_board = init_chinese_chess_board()
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
            action = input("Choose action: 'flip' or 'move': ").strip().lower()

            if action == "flip":
                row, col = map(int, input("Enter row and column to flip (e.g., '1 2'): ").split())
                if not flip_piece(board, hidden_board, row, col):
                    print("Invalid flip.")
                    continue
                socket.send(f"flip {row} {col}".encode())
            elif action == "move":
                move = input("Enter your move (e.g., '0 1 1 1' for moving from (0,1) to (1,1)): ")
                start_row, start_col, end_row, end_col = map(int, move.split())

                if not is_valid_move_dark_chess(board, start_row, start_col, end_row, end_col, current_player):
                    print("Invalid move. Please try again.")
                    continue

                # Move the piece
                board[end_row][end_col] = board[start_row][start_col]
                board[start_row][start_col] = " "
                socket.send(f"move {move}".encode())
            else:
                print("Invalid action.")
                continue
        else:
            print(f"Waiting for Player {opponent}'s action...")
            data = socket.recv(1024).decode()
            action, *params = data.split()

            if action == "flip":
                row, col = map(int, params)
                flip_piece(board, hidden_board, row, col)
            elif action == "move":
                start_row, start_col, end_row, end_col = map(int, params)
                board[end_row][end_col] = board[start_row][start_col]
                board[start_row][start_col] = " "

        current_player = opponent if current_player == Me else Me
