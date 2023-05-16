import numpy as np
import math
import random
from constants import (
    ROW,
    COL,
    PLAYER_PIECE,
    AI_PIECE,
    EMPTY,
    WINDOW_LEN,
)


def createBoard():
    board = np.zeros((ROW, COL))
    return board


def dropPiece(board, row, col, piece):
    board[row][col] = piece


def isValidLoc(board, col):
    return board[ROW - 1][col] == 0


def getNextOpenRow(board, col):
    for r in range(ROW):
        if board[r][col] == 0:
            return r


def printBoard(board):
    print(np.flip(board, 0))


def winMove(board, piece):
    # Check horizontal locations for win
    for c in range(COL - 3):
        for r in range(ROW):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True

    # Check vertical locations for win
    for c in range(COL):
        for r in range(ROW - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c] == piece
                and board[r + 2][c] == piece
                and board[r + 3][c] == piece
            ):
                return True

    # Check positively sloped diagonals
    for c in range(COL - 3):
        for r in range(ROW - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c + 1] == piece
                and board[r + 2][c + 2] == piece
                and board[r + 3][c + 3] == piece
            ):
                return True

    # Check negatively sloped diagonals
    for c in range(COL - 3):
        for r in range(3, ROW):
            if (
                board[r][c] == piece
                and board[r - 1][c + 1] == piece
                and board[r - 2][c + 2] == piece
                and board[r - 3][c + 3] == piece
            ):
                return True


def evalWindow(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def scorePos(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COL // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COL - 3):
            window = row_array[c : c + WINDOW_LEN]
            score += evalWindow(window, piece)

    ## Score Vertical
    for c in range(COL):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW - 3):
            window = col_array[r : r + WINDOW_LEN]
            score += evalWindow(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW - 3):
        for c in range(COL - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LEN)]
            score += evalWindow(window, piece)

    for r in range(ROW - 3):
        for c in range(COL - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LEN)]
            score += evalWindow(window, piece)

    return score


def getValidLocs(board):
    valid_locations = []
    for col in range(COL):
        if isValidLoc(board, col):
            valid_locations.append(col)
    return valid_locations


def getBestMove(board, piece):
    valid_locations = getValidLocs(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = getNextOpenRow(board, col)
        temp_board = board.copy()
        dropPiece(temp_board, row, col, piece)
        score = scorePos(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col


def isTerminalNode(board):
    return (
        winMove(board, PLAYER_PIECE)
        or winMove(board, AI_PIECE)
        or len(getValidLocs(board)) == 0
    )


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = getValidLocs(board)
    is_terminal = isTerminalNode(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winMove(board, AI_PIECE):
                return (None, 100000000000000)
            elif winMove(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # No more valid moves (Game Over)
                return (None, 0)
        else:  # Depth = 0
            return (None, scorePos(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = getNextOpenRow(board, col)
            b_copy = board.copy()
            dropPiece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing Player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = getNextOpenRow(board, col)
            b_copy = board.copy()
            dropPiece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def isInRect(pos, rect):
    x, y = pos
    return rect.left < x < rect.right and rect.top < y < rect.bottom
