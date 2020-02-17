from random import randint
from BoardClasses import Move
from BoardClasses import Board
from MyBoard import MyBoard
from Heuristic import *
from GravityHeuristic import *

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

MIN_VALUE = -99999999
MAX_VALUE = 99999999
TARGET_DEPTH = 10
PLAYER1 = 1
PLAYER2 = 2
CLEAR = 0
MIN_TURN = 0
MAX_TURN = 1
PURE_MODE = 0
AB_MODE = 1
MODE = 1
RANDOM = False
WIN_CODE = 3000
LOSE_CODE = -3000

depth = {(0, 5): 4, (0, 7): 3, (1, 5): 8, (1, 7): 6}

WEIGHTS = [1, -0.5, 0.1, -1, 0, 0]


def heuristic_random():
    return randint(-100000, 100000)


class StudentAI():
    col = 0
    row = 0
    k = 0
    g = 0
    # player1 is me, player 2 is opponent
    player1 = -1
    player2 = -1

    def __init__(self, col, row, k, g):
        self.g = g
        self.col = col
        self.row = row
        self.k = k
        self.board = Board(col, row, k, g)
        self.myBoard = MyBoard(col, row, k, g)
        self.heuristic = Heuristic(WEIGHTS)
        self.heuristic_g = GravityHeuristic(WEIGHTS)
        global TARGET_DEPTH
        try:
            TARGET_DEPTH = depth[(g, col)]
        except:
            TARGET_DEPTH = 5 if g else 3

    def get_move(self, move):
        if self.player1 == -1:
            if move.col == -1:
                self.player1 = PLAYER1
                self.player2 = PLAYER2

                if self.g == 1:
                    move = [self.col // 2, 0]
                    self.myBoard.move(move[0], move[1], self.player1)
                    return Move(move[0], move[1])
                else:
                    move = [self.col // 2, self.row // 2]
                    self.myBoard.move(move[0], move[1], self.player1)
                    return Move(move[0], move[1])
            else:
                self.player1 = PLAYER2
                self.player2 = PLAYER1

        # help your opponent move XD
        if move.col != -1 and move.row != -1:
            if self.g == 0:
                self.myBoard.move(move.col, move.row, self.player2)
            else:
                r = self.myBoard.get_row_with_g(move.col)
                self.myBoard.move(move.col, r, self.player2)

        move = [-1, -1]

        if MODE == PURE_MODE:
            move, _ = self.pure_minimax(0, MAX_TURN, move)
        else:
            move, _ = self.ab_minimax(0, MAX_TURN, MIN_VALUE, MAX_VALUE, move)

        self.myBoard.move(move[0], move[1], self.player1)

        # g = 1 has gravity, 0 no gravity
        if self.g == 0:
            return Move(move[0], move[1])
        # no gravity
        else:
            return Move(move[0], 0)

    def pure_minimax(self, cur_depth, turn, move):
        """
        :return: move, h
        """
        # base case : targetDepth reached
        if cur_depth == TARGET_DEPTH:
            h = self.cal_heru()
            return h

        h = MIN_VALUE if turn == MAX_TURN else MAX_VALUE

        player = self.player1 if turn == MAX_TURN else self.player2

        # g = 1 has gravity, 0 no gravity
        if self.g == 0:
            for a in range(self.col):
                i = (self.col + (~a, a)[a % 2]) // 2
                for b in range(self.row):
                    j = (self.row + (~b, b)[b % 2]) // 2
                    # update move only when valid
                    if self.myBoard.is_valid_move(i, j, True):
                        move, h = self.pure_update_move_h(i, j, move, h, turn, cur_depth, player)

        # with gravity
        else:
            for a in range(self.col):
                i = (self.col + (~a, a)[a % 2]) // 2

                j = self.myBoard.get_row_with_g(i)

                if j == -1:
                    continue

                move, h = self.pure_update_move_h(i, j, move, h, turn, cur_depth, player)

        return move, h

    def pure_update_move_h(self, col, row, move, h, turn, cur_depth, player):
        # make move
        self.myBoard.move(col, row, player)

        if turn == MAX_TURN:
            _, h_star = self.pure_minimax(cur_depth + 1, MIN_TURN, move)
            if h_star > h:
                move[0] = col
                move[1] = row
                h = h_star

        else:
            _, h_star = self.pure_minimax(cur_depth + 1, MAX_TURN, move)
            if h_star < h:
                move[0] = col
                move[1] = row
                h = h_star

        # clear move
        self.myBoard.clear_move(col, row)

        return move, h

    def ab_minimax(self, cur_depth, turn, alpha, beta, move):
        """
        :return: move, h
        """
        # check if is target
        if cur_depth == TARGET_DEPTH:
            h = self.cal_heru()
            return h

        h = MIN_VALUE if turn == MAX_TURN else MAX_VALUE
        player = self.player1 if turn == MAX_TURN else self.player2

        break_flag = False

        if self.g == 0:
            for a in range(self.col):
                i = (self.col + (~a, a)[a % 2]) // 2
                for b in range(self.row):
                    j = (self.row + (~b, b)[b % 2]) // 2
                    if self.myBoard.is_valid_move(i, j, True):
                        break_flag, move, h, alpha, beta = self.ab_update_move_h(i, j, move, h, alpha, beta, turn,
                                                                                 cur_depth, player)
                        if break_flag:
                            break
                if break_flag:
                    break

        else:
            for a in range(self.col):
                i = (self.col + (~a, a)[a % 2]) // 2

                j = self.myBoard.get_row_with_g(i)
                if j == -1:
                    continue

                break_flag, move, h, alpha, beta = self.ab_update_move_h(i, j, move, h, alpha, beta, turn, cur_depth,
                                                                         player)
                if break_flag:
                    break

        return move, h

    def ab_update_move_h(self, col, row, move, h, alpha, beta, turn, cur_depth, player):
        break_flag = False

        # make move
        self.myBoard.move(col, row, player)

        if turn == MAX_TURN:
            if self.myBoard.is_win():
                move[0] = col
                move[1] = row
                self.myBoard.clear_move(col, row)

                return True, move, WIN_CODE, alpha, beta

            _, h_star = self.ab_minimax(cur_depth + 1, MIN_TURN, alpha, beta, move)

            if h_star == WIN_CODE:
                move[0] = col
                move[1] = row
                self.myBoard.clear_move(col, row)

                return True, move, WIN_CODE, alpha, beta

            if h_star > h:
                h = h_star
                move[0] = col
                move[1] = row

            alpha = max(alpha, h_star)
        # MIN_TURN
        else:
            if self.myBoard.is_win():
                move[0] = col
                move[1] = row
                self.myBoard.clear_move(col, row)

                return True, move, LOSE_CODE, alpha, beta

            _, h_star = self.ab_minimax(cur_depth + 1, MAX_TURN, alpha, beta, move)

            if h_star == LOSE_CODE:
                move[0] = col
                move[1] = row
                self.myBoard.clear_move(col, row)

                return True, move, LOSE_CODE, alpha, beta

            if h_star < h:
                h = h_star
                move[0] = col
                move[1] = row

            beta = min(beta, h_star)

        if beta <= alpha:
            break_flag = True

        # clear move
        self.myBoard.clear_move(col, row)

        return break_flag, move, h, alpha, beta

    def cal_heru(self):
        if RANDOM:
            return [], heuristic_random()
        else:
            if self.g == 1:
                return [], self.heuristic_g.eval_board(self.player1, self.player2, self.myBoard)
            else:
                return [], self.heuristic.eval_board(Player(self.player1), self.myBoard)
