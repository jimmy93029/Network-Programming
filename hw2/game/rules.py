import random

# Define colors for displaying red and blue pieces
RED = "\033[31m"
BLUE = "\033[34m"
RESET = "\033[0m"


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


def colored_piece(piece):
    """Return the piece with color coding based on its team."""
    red_pieces = "帥仕相車馬砲兵"
    blue_pieces = "将士象车马炮卒"
    
    if piece in red_pieces:
        return RED + piece + RESET
    elif piece in blue_pieces:
        return BLUE + piece + RESET
    else:
        return piece


def print_chinese_chess_board(board):
    """Display the board with flipped pieces and color-coded based on teams."""
    print("  0 1 2 3 4 5 6 7")  # Column indices
    for i, row in enumerate(board):
        colored_row = [colored_piece(cell) for cell in row]
        print(f"{i} " + " ".join(colored_row))


def flip_piece(board, hidden_board, row, col):
    """Flip a piece on the board, revealing its hidden identity."""
    if board[row][col] != "*":
        print("Piece is already flipped!")
        return False
    board[row][col] = hidden_board[row][col]  # Reveal the actual piece
    hidden_board[row][col] = "*"
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
    if player == "A" and piece not in "帥仕相車馬砲兵":
        return False
    if player == "B" and piece not in "将士象车马炮卒":
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
        if player == "A" and target in "帥仕相車馬砲兵":
            print("You can't eat your own piece.")
            return False
        if player == "B" and target in "将士象车马炮卒":
            print("You can't eat your own piece.")
            return False
        if not is_valid_eat(piece, target):
            print("This piece cannot eat the target piece based on the rules.")
            return False

    return True


def is_valid_eat(attacker, defender):
    """Determine if the attacker can eat the defender based on dark chess rules."""
    hierarchy = {
        "帥": ["仕", "相", "車", "馬", "砲"],
        "將": ["士", "象", "车", "马", "炮"],
        "仕": ["相", "車", "馬", "砲", "兵"],
        "士": ["象", "车", "马", "炮", "卒"],
        "相": ["車", "馬", "砲", "兵"],
        "象": ["车", "马", "炮", "卒"],
        "車": ["馬", "砲", "兵"],
        "车": ["马", "炮", "卒"],
        "馬": ["砲", "兵"],
        "马": ["炮", "卒"],
        "砲": ["兵"],
        "炮": ["卒"],
        "兵": ["帥", "將"],
        "卒": ["帥", "將"]
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


def get_board(socket, Me):
    if Me == "A":
        board, hidden_board = init_chinese_chess_board()
        board_data = ",".join("".join(row) for row in hidden_board)
        socket.send(board_data.encode())  # Send encoded hidden_board as a single string
    else:
        board = [["*" for _ in range(8)] for _ in range(4)]
        board_data = socket.recv(1024).decode()
        hidden_board = [list(board_data[i:i+8]) for i in range(0, len(board_data), 8)]

    return board, hidden_board