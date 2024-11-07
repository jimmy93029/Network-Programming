"""Chinese chess rules"""


def is_valid_move_dark_chess(board, start_row, start_col, end_row, end_col, player):
    """Check if a move is valid for dark chess, including flipping or moving/eating."""
    piece = board[start_row][start_col]
    target = board[end_row][end_col]

    # 如果棋子還沒翻開或者空格，無法移動
    if piece == "*" or piece == " ":
        print("No piece to move.")
        return False

    # 確保玩家只能移動自己的棋子
    if player == "A" and piece not in "帥仕相車馬砲兵":
        return False
    if player == "B" and piece not in "将士象车马炮卒":
        return False

    # 針對一般棋子，確認它們是否只能移動一步
    if piece not in "砲炮":  
        if abs(start_row - end_row) + abs(start_col - end_col) != 1:
            print("Pieces can only move one step horizontally or vertically.")
            return False
    elif piece in "砲炮":  
        if not is_valid_cannon_move(board, start_row, start_col, end_row, end_col):
            return False

    # 檢查吃子規則
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
        "帥": ["兵"], "將": ["卒"],  # 帥(將)可以被兵卒吃
        "仕": ["兵", "卒", "車", "馬", "砲", "兵", "卒"],
        "士": ["兵", "卒", "车", "马", "炮", "卒", "兵"],
        "相": ["車", "馬", "砲", "兵", "卒"],  # 相(象)等級較高
        "象": ["车", "马", "炮", "卒", "兵"],
        "車": ["馬", "砲", "兵", "卒"],
        "车": ["马", "炮", "卒", "兵"],
        "馬": ["砲", "兵", "卒"],
        "马": ["炮", "卒", "兵"],
        "砲": ["帥", "仕", "相", "車", "馬", "兵", "卒"],
        "炮": ["將", "士", "象", "车", "马", "卒", "兵"],
        "兵": ["帥", "將"],
        "卒": ["帥", "將"]
    }
    return defender in hierarchy.get(attacker, [])


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


def is_valid_eat(attacker, defender):
    """Determine if the attacker can eat the defender based on dark chess rules."""
    # Define hierarchy for eating
    hierarchy = {
        "帥": ["兵"], "將": ["卒"],  # 帥(將) can be eaten by small soldier
        "仕": ["兵", "卒", "車", "馬", "砲", "兵", "卒"],
        "士": ["兵", "卒", "车", "马", "炮", "卒", "兵"],
        "相": ["車", "馬", "砲", "兵", "卒"],  # 象的等級較高
        "象": ["车", "马", "炮", "卒", "兵"],
        "車": ["馬", "砲", "兵", "卒"],
        "车": ["马", "炮", "卒", "兵"],
        "馬": ["砲", "兵", "卒"],
        "马": ["炮", "卒", "兵"],
        "砲": ["帥", "仕", "相", "車", "馬", "兵", "卒"],
        "炮": ["將", "士", "象", "车", "马", "卒", "兵"],
        "兵": ["帥", "將"],
        "卒": ["帥", "將"]
    }
    return defender in hierarchy.get(attacker, [])


