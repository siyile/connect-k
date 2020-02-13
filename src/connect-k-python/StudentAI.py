from random import randint
from BoardClasses import Move
from BoardClasses import Board
from MyBoard import MyBoard
from Heuristic import *

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

MIN_VALUE: int = -99999999
MAX_VALUE: int = 99999999
TARGET_DEPTH: int = 2
PLAYER1: int = 1
PLAYER2: int = 2
CLEAR: int = 0
MIN_TURN: int = 0
MAX_TURN: int = 1

weights: List[float] = [1, -1, 0, 0, 0, 0]


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
        self.heuristic = Heuristic(weights)

    def get_move(self, move):
        if self.player1 == -1 and move.col == -1:
            self.player1 = PLAYER1
            self.player2 = PLAYER2
        else:
            self.player1 = PLAYER2
            self.player2 = PLAYER1

        # help opponent move XD
        if move.col != -1 and move.row != -1:
            if self.g == 0:
                self.myBoard.move(move.col, move.row, self.player2)
            else:
                r = self.myBoard.get_row_with_g(move.col)
                self.myBoard.move(move.col, move.row, self.player2)

        move = [-1, -1]
        h = MIN_VALUE
        if self.g == 0:
            for i in range(self.col):
                for j in range(self.row):
                    if not self.myBoard.is_valid_move(i, j, True):
                        continue

                    self.myBoard.move(i, j, self.player1)

                    h_star = self.minimax(0, MAX_TURN)
                    if h_star > h:
                        move[0] = i
                        move[1] = j
                        h = h_star

                    self.myBoard.clear_move(i, j)

            self.myBoard.move(move[0], move[1], self.player1)
            return Move(move[0], move[1])
        else:
            for i in range(self.col):
                j = self.myBoard.get_row_with_g(i)

                if j == -1:
                    continue

                self.myBoard.move(i, j, self.player1)

                h_star = self.minimax(0, MAX_TURN)
                if h_star > h:
                    move[0] = i
                    move[1] = j
                    h = h_star

                self.myBoard.clear_move(i, j)

            self.myBoard.move(move[0], move[1], self.player1)
            return Move(move[0], 0)

    def heuristic(self):
        return randint(-100000, 100000)

    def minimax(self, cur_depth, turn):
        # base case : targetDepth reached
        if cur_depth == TARGET_DEPTH:
            return self.heuristic.eval_board(Player(self.player1), self.myBoard)

        # in level 1, do not loop
        if cur_depth == 0:
            return self.minimax(cur_depth + 1, MIN_TURN)

        h = MIN_VALUE if turn == MAX_TURN else MAX_VALUE

        player = self.player1 if turn == MAX_TURN else self.player2

        # g = 1 has gravity, 0 no gravity
        if self.g == 0:
            for i in range(self.col):
                for j in range(self.row):
                    # if current move valid
                    if self.myBoard.is_valid_move(i, j, True):
                        # make move
                        self.myBoard.move(i, j, player)

                        if turn == MAX_TURN:
                            h = max(self.minimax(cur_depth + 1, MIN_TURN), h)

                        else:
                            h = min(self.minimax(cur_depth + 1, MAX_TURN), h)

                        # clear move
                        self.myBoard.clear_move(i, j)

            return h

                    # not valid return MIN OR MAX value, attention turn is current turn
                    # else:
                    #     if turn == MAX_TURN:
                    #         return MAX_VALUE
                    #     else:
                    #         return MIN_VALUE

        else:
            for i in range(self.col):
                j = self.myBoard.get_row_with_g(i)

                if j == -1:
                    continue
                    # if turn == MAX_TURN:
                    #     return MAX_VALUE
                    # else:
                    #     return MIN_VALUE

                # make move
                self.myBoard.move(i, j, self.player1)

                if turn == MAX_TURN:
                    h = max(self.minimax(cur_depth + 1, MIN_TURN), h)

                else:
                    h = min(self.minimax(cur_depth + 1, MAX_TURN), h)

                # clear move
                self.myBoard.clear_move(i, j)

            return h

    def deepcopy_board(self):
        for i in range(self.col):
            for j in range(self.row):
                self.myBoard.board[j][i] = self.board.board[j][i]
