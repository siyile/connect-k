from typing import *
from enum import Enum
from BoardClasses import *

MAX_VALUE = 99999


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
        # score = 0
        # if self.weights[0] != 0:
        #     # p1 winning rows & diags
        #     score += self.weights[0] * self.__winning_chances(player, board)
        # if self.weights[1] != 0:
        #     # p2 winning rows & diags
        #     score += self.weights[1] * self.__winning_chances(player.opposite, board)
        # return score
        score = 0
        r_chances, r_threats = Heuristic.__count_row(player, board)
        c_chances, c_threats = Heuristic.__count_col(player, board)
        d_chances, d_threats = Heuristic.__count_diag(player, board, True)
        ad_chances, ad_threats = Heuristic.__count_diag(player, board, False)
        return self.weights[0] * (r_chances[player.value] + c_chances[player.value] + d_chances[player.value] + ad_chances[player.value]) + \
               self.weights[1] * (r_chances[player.opposite.value] + c_chances[player.opposite.value] + d_chances[player.opposite.value] + ad_chances[player.opposite.value]) + \
               self.weights[2] * (r_threats[player.value] + c_threats[player.value] + d_threats[player.value] + ad_threats[player.value]) + \
               self.weights[3] * (r_threats[player.opposite.value] + c_threats[player.opposite.value] + d_threats[player.opposite.value] + ad_threats[player.opposite.value])

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
                    if val == player.opposite.value:
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
                    if board.board[start_x + dx * delta][start_y + dy * delta] == player.opposite.value:
                        can_win = False
                        break
                if can_win:
                    score += 1
        return score

    @staticmethod
    def __count_row(player: Player, board: Board):
        chances = {1: 0, 2: 0}
        threats = {1: 0, 2: 0}
        for x in range(board.row):
            count = {0: 0, 1: 0, 2: 0}
            for y in range(board.k):
                count[board.board[x][y]] += 1
            y = board.k - 1
            while True:
                Heuristic.__eval_counts(player, board, count, chances, threats)
                # slide window
                y += 1
                if y >= board.col:
                    break
                count[board.board[x][y - board.k]] -= 1
                count[board.board[x][y]] += 1
        return chances, threats

    @staticmethod
    def __count_col(player: Player, board: Board):
        chances = {1: 0, 2: 0}
        threats = {1: 0, 2: 0}
        for y in range(board.col):
            count = {0: 0, 1: 0, 2: 0}
            for x in range(board.k):
                count[board.board[x][y]] += 1
            x = board.k - 1
            while True:
                Heuristic.__eval_counts(player, board, count, chances, threats)
                # slide window
                x += 1
                if x >= board.row:
                    break
                count[board.board[x - board.k][y]] -= 1
                count[board.board[x][y]] += 1
        return chances, threats

    @staticmethod
    def __count_diag(player: Player, board: Board, anti_diag: bool):
        chances = {1: 0, 2: 0}
        threats = {1: 0, 2: 0}
        range_row = range(board.row - board.k + 1) if not anti_diag else range(board.k - 1, board.row)
        dx = 1 if not anti_diag else -1

        for start_x in range_row:
            count = {0: 0, 1: 0, 2: 0}
            for i in range(board.k):
                count[board.board[start_x + dx * i][i]] += 1
            y = board.k - 1
            while True:
                Heuristic.__eval_counts(player, board, count, chances, threats)
                y += 1
                if y >= board.col:
                    break
                count[board.board[start_x + dx * (y - board.k)][y - board.k]] -= 1
                count[board.board[start_x + dx * y][y]] += 1
            return chances, threats


    @staticmethod
    def __eval_counts(player: Player, board: Board, count: Dict[int, int], chances: Dict[int, int],
                      threats: Dict[int, int]):
        if count[player.value] == board.k:  # have already won, no bother further searching
            chances[player.value] = MAX_VALUE
            return
        if count[player.value] > 0 and count[player.opposite.value] == 0:
            chances[player.value] += 1
            if count[player.value] == board.k - 1:
                threats[player.value] += 1
        if count[player.opposite.value] > 0 and count[player.value] == 0:
            chances[player.opposite.value] += 1
            if count[player.opposite.value] == board.k - 1:
                threats[player.opposite.value] += 1


if __name__ == "__main__":
    b = Board(5, 5, 3, 0)
    b.board[0][0] = 1
    b.board[1][0] = 1
    b.show_board(None)
    h = Heuristic([1, -1, 0.1, -0.1, 0, 0])
    print(h.eval_board(Player(1), b))
