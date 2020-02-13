from typing import *
from enum import Enum
from BoardClasses import *


class Player(Enum):
    empty = 0
    me = 1
    op = 2

    @property
    def opposite(self):
        if self == Player.empty:
            raise ValueError("Trying to get opposite player of an empty cell")
        elif self == Player.me:
            return Player.op
        else:
            return Player.me


class Heuristic:
    """
    Heuristic as a linear combination of 6 sub-features, weights defined as List[float]
    """

    def __init__(self, weights: List[float]):
        if len(weights) != 6:
            raise ValueError("len of weights must be 6!")
        self.weights = weights

    def eval_board(self, player: Player, board: Board) -> float:
        score = 0
        if self.weights[0] != 0:
            # p1 winning rows & diags
            score += self.weights[0] * self.__winning_chances(player, board)
        if self.weights[1] != 0:
            # p2 winning rows & diags
            score += self.weights[1] * self.__winning_chances(player.opposite, board)
        return score

    @staticmethod
    def __winning_chances(player: Player, board: Board):
        return Heuristic.__winning_rows(player, True, board) + \
               Heuristic.__winning_rows(player, False, board) + \
               Heuristic.__winning_diags(player, True, board) + \
               Heuristic.__winning_diags(player, False, board)

    @staticmethod
    def __winning_rows(player: Player, horizontal: bool, board: Board) -> int:
        rx = range(board.row) if horizontal else range(board.row - board.k + 1)
        ry = range(board.col - board.k + 1) if horizontal else range(board.col)
        score = 0
        for x in rx:
            for y in ry:
                can_win = True
                for delta in range(board.k):
                    val = board.board[x][y + delta] if horizontal else board.board[x + delta][y]
                    if val == player.opposite:
                        can_win = False
                        break
                if can_win:
                    score += 1
        return score

    @staticmethod
    def __winning_diags(player: Player, anti_diag: bool, board: Board) -> int:
        range_row = range(board.row - board.k + 1) if not anti_diag else range(board.k - 1, board.row)
        range_col = range(board.col - board.k + 1)
        dx = 1 if not anti_diag else -1
        dy = 1
        score = 0
        # top-left to bottom-right
        for start_x in range_row:
            for start_y in range_col:
                can_win = True
                for delta in range(board.k):
                    if board.board[start_x + dx * delta][start_y + dy * delta] == player.opposite:
                        can_win = False
                        break
                if can_win:
                    score += 1
        return score


if __name__ == "__main__":
    b = Board(4, 3, 2, 0)
    h = Heuristic([1, 0, 0, 0, 0, 0])
    print(h.eval_board(Player(1), b))
