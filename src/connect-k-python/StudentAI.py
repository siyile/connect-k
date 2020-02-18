from random import randint
from BoardClasses import Move
from BoardClasses import Board
from MyBoard import MyBoard
from Heuristic import *
from GravityHeuristic import *

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

PLAYER1 = 1
PLAYER2 = 2
CLEAR = 0
MIN_TURN = 0
MAX_TURN = 1
RANDOM = False
WIN_CODE = 2000000
LOSE_CODE = -WIN_CODE
MAX_VALUE = 100000
MIN_VALUE = -MAX_VALUE


depth = {(0, 5): 4, (0, 7): 3, (1, 5): 8, (1, 7): 8, (1, 6): 7, (1, 8): 5}

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
    
    limit = 10

    def __init__(self, col, row, k, g):
        self.g = g
        self.col = col
        self.row = row
        self.k = k
        self.board = Board(col, row, k, g)
        self.myBoard = MyBoard(col, row, k, g)
        self.heuristic = Heuristic(WEIGHTS)
        self.heuristic_g = GravityHeuristic(WEIGHTS)
        try:
            self.limit = depth[(g, col)]
        except:
            self.limit = 5 if g else 3

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

        move, h = self.ab_minimax(self.limit, MAX_TURN, MIN_VALUE, MAX_VALUE)

        if h == LOSE_CODE or h == MIN_VALUE:
            move, h = self.ab_minimax(2, MAX_TURN, MIN_VALUE, MAX_VALUE)

        self.myBoard.move(move[0], move[1], self.player1)

        # g = 1 has gravity, 0 no gravity
        if self.g == 0:
            return Move(move[0], move[1])
        # no gravity
        else:
            return Move(move[0], 0)

    def ab_minimax(self, cur_depth, turn, alpha, beta):
        """
        :return: move, h
        """
        # check if is target
        if cur_depth == 0:
            h = self.cal_heru()
            return h

        h = MIN_VALUE if turn == MAX_TURN else MAX_VALUE
        player = self.player1 if turn == MAX_TURN else self.player2

        break_flag = False
        move = [-1, -1]

        # TODO: remove
        if cur_depth == self.limit:
            heuristic_list = [[0 for x in range(self.col)] for y in range (self.row)]

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
        # with gravity
        else:
            for a in range(self.col):
                i = (self.col + (~a, a)[a % 2]) // 2

                j = self.myBoard.get_row_with_g(i)
                if j == -1:
                    continue

                col = i
                row = j

                # make move
                self.myBoard.move(col, row, player)

                if turn == MAX_TURN:
                    winner = self.myBoard.is_win()
                    if winner == self.player1 or winner == -1:
                        move[0] = col
                        move[1] = row
                        self.myBoard.clear_move(col, row)

                        # TODO: remove
                        if cur_depth == self.limit:
                            heuristic_list[row][col] = WIN_CODE

                        return move, WIN_CODE
                    elif winner == self.player2:
                        h = max(LOSE_CODE, h)
                    else:
                        _, h_star = self.ab_minimax(cur_depth - 1, MIN_TURN, alpha, beta)
                        # TODO: remove
                        if cur_depth == self.limit:
                            heuristic_list[row][col] = h

                        if h_star > h:
                            h = h_star
                            move[0] = col
                            move[1] = row

                    alpha = max(alpha, h)

                # MIN_TURN
                else:
                    winner = self.myBoard.is_win()
                    if winner == self.player2:
                        self.myBoard.clear_move(col, row)
                        return [], LOSE_CODE
                    elif winner == self.player1:
                        h = min(h, WIN_CODE)
                    else:
                        _, h_star = self.ab_minimax(cur_depth - 1, MAX_TURN, alpha, beta)

                        h = min(h_star, h)

                    beta = min(beta, h)

                # clear move
                self.myBoard.clear_move(col, row)

                if beta <= alpha:
                    break

        # TODO: remove
        if self.limit == cur_depth:
            self.print_heuristic(heuristic_list)

        return move, h

    def print_heuristic(self, h):
        for row in range(self.row):
            print(str(row).ljust(8), end='')
            for col in range(self.col):
                if h[row][col] == WIN_CODE:
                    s = "WIN"
                elif h[row][col] == LOSE_CODE:
                    s = "LOSE"
                else:
                    s = str(h[row][col])
                print(s.ljust(8), end='')
            print()
        print(''.ljust(100, '-'))

        print(''.ljust(8), end='')
        for i in range(self.col):
            print(str(i).ljust(8), end='')

        print()
        print()

    def ab_update_move_h(self, col, row, move, h, alpha, beta, turn, cur_depth, player):
        break_flag = False

        # make move
        self.myBoard.move(col, row, player)

        if turn == MAX_TURN:
            if self.myBoard.is_win() == self.player1:
                move[0] = col
                move[1] = row
                self.myBoard.clear_move(col, row)

                return True, move, WIN_CODE, alpha, beta

            _, h_star = self.ab_minimax(cur_depth - 1, MIN_TURN, alpha, beta)

            if h_star == WIN_CODE:
                move[0] = col
                move[1] = row
                self.myBoard.clear_move(col, row)

                return True, move, WIN_CODE, alpha, beta

            elif h_star != LOSE_CODE:
                if h_star > h:
                    h = h_star
                    move[0] = col
                    move[1] = row

                alpha = max(alpha, h_star)
        # MIN_TURN
        else:
            if self.myBoard.is_win() == self.player2:
                move[0] = col
                move[1] = row
                self.myBoard.clear_move(col, row)

                return True, move, LOSE_CODE, alpha, beta

            _, h_star = self.ab_minimax(cur_depth - 1, MAX_TURN, alpha, beta)

            if h_star == LOSE_CODE:
                move[0] = col
                move[1] = row
                self.myBoard.clear_move(col, row)

                return True, move, LOSE_CODE, alpha, beta

            elif h_star != WIN_CODE:
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
