from BoardClasses import *


class MyBoard(Board):
    def __init__(self, col, row, k, g):
        Board.__init__(self, col, row, k, g)

    def check_space(self, c, r):
        return True if self.board[r][c] == 0 else False

    def move(self, col, row, player):
        if type(player) is not int or (player != 1 and player != 2):
            raise InvalidMoveError()
        if not self.is_valid_move(col, row):
            raise InvalidMoveError()
        self.board[row][col] = player

    def get_row_with_g(self, col):
        for i in range(self.row - 1, -1, -1):
            if self.check_space(col, i):
                return i
        return -1

    def clear_move(self, col, row):
        self.board[row][col] = 0

    def get_slot(self, c, r):
        return self.board[r][c]
