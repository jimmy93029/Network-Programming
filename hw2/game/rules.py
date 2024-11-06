"""Chinese chess rules"""


def init_chinese_chess_board():
    """Initialized chess board"""
    board = [
        ["車", "馬", "相", "仕", "帥", "仕", "相", "馬", "車"],
        [" ", " ", " ", " ", " ", " ", " ", " ", " "],
        [" ", "砲", " ", " ", " ", " ", " ", "砲", " "],
        ["兵", " ", "兵", " ", "兵", " ", "兵", " ", "兵"],
        [" ", " ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " ", " "],
        ["卒", " ", "卒", " ", "卒", " ", "卒", " ", "卒"],
        [" ", "炮", " ", " ", " ", " ", " ", "炮", " "],
        [" ", " ", " ", " ", " ", " ", " ", " ", " "],
        ["車", "馬", "象", "士", "將", "士", "象", "馬", "車"]
    ]
    return board


def print_chinese_chess_board(board):
    """dispaly board"""
    print("  0 1 2 3 4 5 6 7 8")   # Also display index
    for i, row in enumerate(board):
        print(f"{i} " + " ".join(row))


def is_valid_move_chinese_chess(board, start_row, start_col, end_row, end_col, player):
    piece = board[start_row][start_col]
    if player == "A" and piece not in "車馬相仕帥砲兵":
        return False
    if player == "B" and piece not in "车马象士将炮卒":
        return False

    if piece in "帥将":
        return is_valid_general_move(start_row, start_col, end_row, end_col, board)
    elif piece in "仕士":
        return is_valid_advisor_move(start_row, start_col, end_row, end_col)
    elif piece in "相象":
        return is_valid_elephant_move(start_row, start_col, end_row, end_col, board, player)
    elif piece in "馬马":
        return is_valid_knight_move(start_row, start_col, end_row, end_col, board)
    elif piece in "車车":
        return is_valid_rook_move(board, start_row, start_col, end_row, end_col)
    elif piece in "砲炮":
        return is_valid_cannon_move(board, start_row, start_col, end_row, end_col)
    elif piece in "兵卒":
        return is_valid_pawn_move(start_row, start_col, end_row, end_col, player)
    return False


# General move function for 帥 or 将; only moves within the "palace" and can directly capture each other.
def is_valid_general_move(start_row, start_col, end_row, end_col, board):
    if end_col < 3 or end_col > 5 or (end_row < 7 and board[start_row][start_col] == "將") or (end_row > 2 and board[start_row][start_col] == "帥"):
        return False
    return (abs(end_row - start_row) == 1 and start_col == end_col) or (abs(end_col - start_col) == 1 and start_row == end_row) or \
           (start_col == end_col and not any(board[r][start_col] != " " for r in range(min(start_row, end_row) + 1, max(start_row, end_row))))


# Advisor move function for 仕 or 士; moves diagonally within the palace.
def is_valid_advisor_move(start_row, start_col, end_row, end_col):
    if end_col < 3 or end_col > 5 or (end_row < 7 and end_row > 9) or (end_row > 2 and end_row < 0):
        return False
    return abs(end_row - start_row) == 1 and abs(end_col - start_col) == 1


# Elephant move function for 相 or 象; moves in a "田" shape, cannot cross the river, and is blocked by pieces in the center of "田".
def is_valid_elephant_move(start_row, start_col, end_row, end_col, board, player):
    if player == "A" and end_row < 5 or player == "B" and end_row > 4:
        return False
    if abs(end_row - start_row) == 2 and abs(end_col - start_col) == 2:
        mid_row, mid_col = (start_row + end_row) // 2, (start_col + end_col) // 2
        return board[mid_row][mid_col] == " "
    return False


# Knight move function for 馬; moves in a "日" shape and is blocked by adjacent pieces.
def is_valid_knight_move(start_row, start_col, end_row, end_col, board):
    row_diff, col_diff = abs(end_row - start_row), abs(end_col - start_col)
    if row_diff == 2 and col_diff == 1:
        return board[start_row + (end_row - start_row) // 2][start_col] == " "
    if row_diff == 1 and col_diff == 2:
        return board[start_row][start_col + (end_col - start_col) // 2] == " "
    return False


# Rook move function for 車; moves in straight lines with no obstruction.
def is_valid_rook_move(board, start_row, start_col, end_row, end_col):
    if start_row != end_row and start_col != end_col:
        return False
    if start_row == end_row:
        step = 1 if start_col < end_col else -1
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] != " ":
                return False
    else:
        step = 1 if start_row < end_row else -1
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] != " ":
                return False
    return True


# Cannon move function for 砲; moves like 車 but requires exactly one piece to jump over when capturing.
def is_valid_cannon_move(board, start_row, start_col, end_row, end_col):
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


# Pawn move function for 兵 or 卒; moves forward before crossing the river and can move sideways after crossing.
def is_valid_pawn_move(start_row, start_col, end_row, end_col, player):
    if player == "A":
        if start_row <= 4:
            return end_row == start_row + 1 and start_col == end_col
        else:
            return (end_row == start_row and abs(end_col - start_col) == 1) or (end_row == start_row + 1 and start_col == end_col)
    else:
        if start_row >= 5:
            return end_row == start_row - 1 and start_col == end_col
        else:
            return (end_row == start_row and abs(end_col - start_col) == 1) or (end_row == start_row - 1 and start_col == end_col)
