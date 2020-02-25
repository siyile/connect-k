from random import randint
from typing import *
from BoardClasses import *
from abc import *

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

PLAYER1 = 1
PLAYER2 = 2
CLEAR = 0
MIN_TURN = 0
MAX_TURN = 1
RANDOM = False
WIN_CODE = 2000
LOSE_CODE = -WIN_CODE
MAX_VALUE = 1000000
MIN_VALUE = -MAX_VALUE


DEPTH = {(0, 5): 5, (0, 7): 4, (1, 5): 9, (1, 7): 7}
WEIGHTS = [1, -0.5, 0.1, -1, 0, 0]

# MAX_VALUE = 99999
# WIN_CODE = 300000
# LOSE_CODE = -300000


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


"""
============================
        Heuristic
============================
"""
class Heuristic(ABC):
    def __init__(self, weights: List[float]):
        if len(weights) != 6:
            raise ValueError("len of weights must be 6!")
        self.weights = weights

    @abstractmethod
    def eval_board(self, player: int, board: MyBoard):
        pass


class NonGravityHeuristic(Heuristic):
    """
    Non-gravity heuristic function as a linear combination of 6 sub-features, weights defined as List[float]
    """

    def __init__(self, weights: List[float]):
        super().__init__(weights)

    def eval_board(self, player: int, board: Board) -> float:
        opponent = player ^ 3
        r_chances, r_threats = self.__count_row(player, board)
        c_chances, c_threats = self.__count_col(player, board)
        d_chances, d_threats = self.__count_diag(player, board, True)
        ad_chances, ad_threats = self.__count_diag(player, board, False)
        return self.weights[0] * (r_chances[player] + c_chances[player] + d_chances[player] + ad_chances[player]) + \
               self.weights[1] * (r_chances[opponent] + c_chances[opponent] + d_chances[opponent] + ad_chances[opponent]) + \
               self.weights[2] * (r_threats[player] + c_threats[player] + d_threats[player] + ad_threats[player]) + \
               self.weights[3] * (r_threats[opponent] + c_threats[opponent] + d_threats[opponent] + ad_threats[opponent])

    def __count_row(self, player: int, board: Board):
        chances = {1: 0, 2: 0}
        threats = {1: 0, 2: 0}
        for x in range(board.row):
            count = {0: 0, 1: 0, 2: 0}
            for y in range(board.k):
                count[board.board[x][y]] += 1
            y = board.k - 1
            while True:
                self.__eval_counts(player, board, count, chances, threats)
                # slide window
                y += 1
                if y >= board.col:
                    break
                count[board.board[x][y - board.k]] -= 1
                count[board.board[x][y]] += 1
        return chances, threats

    def __count_col(self, player: int, board: Board):
        chances = {1: 0, 2: 0}
        threats = {1: 0, 2: 0}
        for y in range(board.col):
            count = {0: 0, 1: 0, 2: 0}
            for x in range(board.k):
                count[board.board[x][y]] += 1
            x = board.k - 1
            while True:
                self.__eval_counts(player, board, count, chances, threats)
                # slide window
                x += 1
                if x >= board.row:
                    break
                count[board.board[x - board.k][y]] -= 1
                count[board.board[x][y]] += 1
        return chances, threats

    def __count_diag(self, player: int, board: Board, anti_diag: bool):
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
                self.__eval_counts(player, board, count, chances, threats)
                y += 1
                if y >= board.col:
                    break
                count[board.board[start_x + dx * (y - board.k)][y - board.k]] -= 1
                count[board.board[start_x + dx * y][y]] += 1
            return chances, threats

    @staticmethod
    def __eval_counts(player: int, board: Board, count: Dict[int, int], chances: Dict[int, int],
                      threats: Dict[int, int]):
        opponent = player ^ 3
        if count[player] == board.k:  # have already won, no bother further searching
            chances[player] = MAX_VALUE
            return
        if count[player] > 0 and count[opponent] == 0:
            chances[player] += 1
            if count[player] == board.k - 1:
                threats[player] += 1
        if count[opponent] > 0 and count[player] == 0:
            chances[opponent] += 1
            if count[opponent] == board.k - 1:
                threats[opponent] += 1
                if not board.g:
                    threats[opponent] = MAX_VALUE

"""
============================
    Gravity Heuristic
============================
"""


class Slot:
    row = -1
    col = -1

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __key(self):
        return self.row, self.col

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.__key() == other.__key()
        return NotImplemented


class Threat:
    unshared_odd = 0
    unshared_even = 0
    shared_odd = 0
    shared_even = 0


class GravityHeuristic(Heuristic):
    """
    Gravity Heuristic
    """
    board = None
    player = 0
    opponent = 0

    player_lines = []
    opponent_lines = []

    player_threat = set()
    opponent_threat = set()

    player_threat_cnt = Threat()
    opponent_threat_cnt = Threat()

    col = 0
    row = 0
    k = 0

    def __init__(self, weights: List[float]):
        super().__init__(weights)

    def eval_board(self, player, board: MyBoard):
        self.col = board.col
        self.row = board.row
        self.k = board.k

        # init board
        # TRASH project structure
        self.board = board
        self.player = player
        self.opponent = player ^ 3

        self.player_lines = [0] * (board.k + 1)
        self.opponent_lines = [0] * (board.k + 1)

        self.player_threat = set()
        self.opponent_threat = set()

        # eval player & opponent horizontal
        self.__eval_horizontal_lines(True)
        self.__eval_horizontal_lines(False)

        # eval player & opponent vertical
        self.__eval_vertical_lines(True)
        self.__eval_vertical_lines(False)

        # eval diagonals
        self.__eval_left_top_diagonals(True)
        self.__eval_top_right_diagonals(True)
        self.__eval_left_top_diagonals(False)
        self.__eval_top_right_diagonals(False)

        # calculate threats count
        player_threat_cnt = self.__calculate_threats(self.player_threat, self.opponent_threat)
        opponent_threat_cnt = self.__calculate_threats(self.opponent_threat, self.player_threat)

        score = 0
        if self.player == 1:
            score += self.__calculate_score(player_threat_cnt, opponent_threat_cnt)
        else:
            score -= self.__calculate_score(opponent_threat_cnt, player_threat_cnt)

        return self.__get_heuristic(score)

    def __eval_horizontal_lines(self, is_player: bool):
        player, opponent, empty = self.__init_player_and_empty_slot(is_player)

        for i in range(self.row):
            for j in range(0, self.col - self.k + 1, 1):
                cnt = 0
                stop_flag = False
                cur_col = j
                while cur_col < j + self.k and not stop_flag:
                    if self.board.get_slot(cur_col, i) == player:
                        cnt += 1
                    elif self.board.get_slot(cur_col, i) == opponent:
                        stop_flag = True
                    else:
                        empty = Slot(i, cur_col)

                    cur_col += 1

                if not stop_flag:
                    self.__add_threat(is_player, empty, cnt)

    def __eval_vertical_lines(self, is_player: bool):
        player, opponent, empty = self.__init_player_and_empty_slot(is_player)

        for j in range(self.col):
            for i in range(self.row - 1, -1, self.k - 2):
                cnt = 0
                stop_flag = False
                cur_row = i
                while i - cur_row + 1 <= self.k and not stop_flag:
                    if self.board.get_slot(j, cur_row) == player:
                        cnt += 1
                    elif self.board.get_slot(j, cur_row) == opponent:
                        stop_flag = True
                    else:
                        empty = Slot(cur_row, j)

                    cur_row -= 1

                if not stop_flag:
                    self.__add_threat(is_player, empty, cnt)

    def __eval_top_right_diagonals(self, is_player: bool):
        player, opponent, empty = self.__init_player_and_empty_slot(is_player)

        for i in range(self.row - 1, -1, self.k - 2):
            for j in range(0, 1, self.col - self.k + 1):
                cnt = 0
                stop_flag = False
                cur_row = i
                cur_col = j

                while cur_row > i - self.k and cur_col < j + self.k and not stop_flag:
                    if self.board.get_slot(cur_col, cur_row) == player:
                        cnt += 1
                    elif self.board.get_slot(cur_col, cur_row) == opponent:
                        stop_flag = True
                    else:
                        empty = Slot(cur_row, cur_col)

                    cur_row -= 1
                    cur_col += 1

                if not stop_flag:
                    self.__add_threat(is_player, empty, cnt)

    def __eval_left_top_diagonals(self, is_player: bool):
        player, opponent, empty = self.__init_player_and_empty_slot(is_player)

        for i in range(self.row - 1, -1, self.k - 2):
            for j in range(self.col - 1, -1, self.k - 2):
                cnt = 0
                stop_flag = False
                cur_row = i
                cur_col = j

                while cur_row > i - self.k and cur_col > j - self.k and not stop_flag:
                    if self.board.get_slot(cur_col, cur_row) == player:
                        cnt += 1
                    elif self.board.get_slot(cur_col, cur_row) == opponent:
                        stop_flag = True
                    else:
                        empty = Slot(cur_row, cur_col)

                    cur_col -= 1
                    cur_row -= 1

                if not stop_flag:
                    self.__add_threat(is_player, empty, cnt)

    def __init_player_and_empty_slot(self, is_player: bool):
        player = self.player if is_player else self.opponent
        opponent = self.opponent if is_player else self.player
        empty = Slot(self.row - 1, 0)
        return player, opponent, empty

    def __add_threat(self, is_player: bool, empty, cnt, is_vertical: bool = False):
        """
        add threat into corresponding target
        """

        """
        if the slot below the last empty is 0, this is a threat
        e.g. k = 3
        X 1 1
        0 2 2
        if X = 0 now we have threat at X
        """
        if cnt == self.k - 1 and empty.row < self.row - 1 and \
                self.board.get_slot(empty.col, empty.row + 1) == 0:
            if is_player and empty not in self.player_threat:
                self.player_threat.add(empty)
            elif not is_player and empty not in self.opponent_threat:
                self.opponent_threat.add(empty)

        if cnt > 0:
            if is_player:
                self.player_lines[cnt] += 1
            else:
                self.opponent_lines[cnt] += 1

    def __calculate_threats(self, player_threats: Set[Slot], opponent_threats: Set[Slot]):
        player_threats_cnt = Threat()

        unshared_odd = set()
        unshared_even = set()
        shared_odd = set()
        shared_even = set()

        for player_threat in player_threats:
            shared = False
            for opponent_threat in opponent_threats:
                if player_threat.col == opponent_threat.col and player_threat.row <= opponent_threat.row:
                    shared = True
                    break

            if shared:
                if (self.row - player_threat.row) % 2 == 1 and player_threat.col not in shared_odd:
                    player_threats_cnt.shared_odd += 1
                    shared_odd.add(player_threat.col)
                elif (self.row - player_threat.row) % 2 == 0 and player_threat.col not in shared_even:
                    player_threats_cnt.shared_even += 1
                    shared_even.add(player_threat.col)
            else:
                if (self.row - player_threat.row) % 2 == 1 and player_threat.col not in unshared_odd:
                    player_threats_cnt.unshared_odd += 1
                    unshared_odd.add(player_threat.col)
                elif (self.row - player_threat.row) % 2 == 0 and player_threat.col not in unshared_even:
                    player_threats_cnt.unshared_even += 1
                    unshared_even.add(player_threat.col)

        return player_threats_cnt

    def __calculate_score(self, pcnt: Threat, ocnt: Threat):
        player_score = 0
        opponent_score = 0

        if self.row % 2 == 0:
            if (pcnt.unshared_odd - 1) == ocnt.unshared_odd or \
                    (pcnt.unshared_odd == ocnt.unshared_odd) and (pcnt.shared_odd % 2 == 1) or \
                    ocnt.unshared_odd == 0 and (pcnt.shared_odd + pcnt.unshared_odd) % 2 == 1:
                player_score += 100
            if (pcnt.unshared_odd + pcnt.shared_odd) == 0 and (ocnt.shared_even + ocnt.unshared_even) > 0 or \
                    (ocnt.unshared_odd - 2) == pcnt.unshared_odd or \
                    (pcnt.unshared_odd == ocnt.unshared_odd) and (ocnt.shared_odd % 2 == 0 and ocnt.shared_odd > 0) or \
                    (ocnt.unshared_odd - 1) == pcnt.unshared_odd and ocnt.shared_odd > 0 or \
                    pcnt.unshared_odd == 0 and (ocnt.unshared_odd == 1 and ocnt.shared_odd > 0) or \
                    ((ocnt.unshared_odd + ocnt.shared_odd) % 2 == 0 and (ocnt.unshared_odd + ocnt.shared_odd) > 0) and pcnt.unshared_odd == 0:
                opponent_score += 100

        elif (self.row * self.col) % 2 == 0 and self.row % 2 == 1:
            if (pcnt.unshared_even - 1) == ocnt.unshared_even or \
                    pcnt.shared_even % 2 == 1 or \
                    (pcnt.shared_even + pcnt.unshared_even) == 1 and (ocnt.shared_odd + ocnt.unshared_odd) == 1:
                player_score += 100

            if (ocnt.shared_odd + ocnt.unshared_odd) > 0 or \
                    (((ocnt.shared_even + ocnt.unshared_even) % 2 == 0 and (ocnt.shared_even + ocnt.unshared_even) > 0) and (((ocnt.unshared_even - 2) == pcnt.unshared_even) or (ocnt.shared_even == pcnt.shared_even))):
                opponent_score += 100

        elif (self.row * self.col) % 2 == 1:
            if ((pcnt.shared_odd + pcnt.unshared_odd) > 0) or \
                    (((pcnt.shared_even + pcnt.unshared_even) % 2 == 0 and (pcnt.shared_even + pcnt.unshared_even) > 0) and ((pcnt.unshared_even - 2 == ocnt.unshared_even) or (pcnt.shared_even == ocnt.shared_even))):
                player_score += 100

            if (ocnt.unshared_even - 1 == pcnt.unshared_even) or \
                    (ocnt.shared_even % 2 == 1) or ((ocnt.shared_even + ocnt.unshared_even) == 1 and (pcnt.shared_odd + pcnt.unshared_odd) == 1):
                opponent_score += 100

        return player_score - opponent_score

    def __get_heuristic(self, h):
        if self.opponent_lines[self.k] > 0:
            return LOSE_CODE
        if self.player_lines[self.k] > 0:
            return WIN_CODE

        multiplier = 1
        for i in range(2, self.k, 1):
            h += multiplier * self.player_lines[i]
            h -= multiplier * self.opponent_lines[i]
            multiplier += 1

        if h == 0:
            if self.player == 2:
                return 1
            else:
                return -1

        return h

"""
============================
        StudentAI
============================
"""
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
        self.heuristic = GravityHeuristic(WEIGHTS) if g else NonGravityHeuristic(WEIGHTS)
        try:
            self.limit = DEPTH[(g, col)]
        except:
            self.limit = 5 if g else 3

    def get_move(self, move):
        if self.player1 == -1:
            if move.col == -1:
                self.player1 = PLAYER1
                self.player2 = PLAYER2

                if self.g == 1:
                    move = [self.col // 2, self.row - 1]
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

        valid_move = False
        depth = self.limit - 1
        while (not valid_move) and depth > 0:
            try:
                self.myBoard.move(move[0], move[1], self.player1)
                valid_move = True
            except InvalidMoveError:
                move, h = self.ab_minimax(depth, MAX_TURN, MIN_VALUE, MAX_VALUE)
                depth -= 1

        print('My turn! I play col: {}, row: {}\n Your turn plz XD!'.format(move[0], move[1]))
        print()

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
            h = self.cal_heuristic()
            return h

        h = MIN_VALUE if turn == MAX_TURN else MAX_VALUE
        player = self.player1 if turn == MAX_TURN else self.player2

        move = [-1, -1]

        # TODO: remove
        if cur_depth == self.limit:
            heuristic_list = [[0 for x in range(self.col)] for y in range(self.row)]

        # without gravity
        if self.g == 0:
            for a in range(self.col):
                i = (self.col + (~a, a)[a % 2]) // 2
                for b in range(self.row):
                    j = (self.row + (~b, b)[b % 2]) // 2

                    col = i
                    row = j

                    if not self.myBoard.check_space(col, row):
                        continue

                    # make move
                    self.myBoard.move(col, row, player)

                    # MAX_TURN
                    if turn == MAX_TURN:
                        winner = self.myBoard.is_win()
                        if winner == self.player1 or winner == -1:
                            move[0] = col
                            move[1] = row
                            self.myBoard.clear_move(col, row)

                            # TODO: remove
                            if cur_depth == self.limit:
                                heuristic_list[row][col] = WIN_CODE
                                self.print_heuristic(heuristic_list)

                            return move, WIN_CODE
                        elif winner == self.player2:
                            h = max(LOSE_CODE, h)
                        else:
                            _, h_star = self.ab_minimax(cur_depth - 1, MIN_TURN, alpha, beta)

                            if h_star > h:
                                h = h_star
                                move[0] = col
                                move[1] = row

                            # TODO: remove
                            if cur_depth == self.limit:
                                heuristic_list[row][col] = h

                        if h != MAX_VALUE:
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

                        if h != MIN_VALUE:
                            beta = min(beta, h)

                    # clear move
                    self.myBoard.clear_move(col, row)

                    if beta <= alpha:
                        break
                if beta <= alpha:
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

                # MAX_TURN
                if turn == MAX_TURN:
                    winner = self.myBoard.is_win()
                    if winner == self.player1 or winner == -1:
                        move[0] = col
                        move[1] = row
                        self.myBoard.clear_move(col, row)

                        # TODO: remove
                        if cur_depth == self.limit:
                            heuristic_list[row][col] = WIN_CODE
                            self.print_heuristic(heuristic_list)

                        return move, WIN_CODE
                    elif winner == self.player2:
                        h = max(LOSE_CODE, h)
                    else:
                        _, h_star = self.ab_minimax(cur_depth - 1, MIN_TURN, alpha, beta)

                        if h_star > h:
                            h = h_star
                            move[0] = col
                            move[1] = row

                        # TODO: remove
                        if cur_depth == self.limit:
                            heuristic_list[row][col] = h

                    if h != MAX_VALUE:
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

                    if h != MIN_VALUE:
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

    def cal_heuristic(self):
        if RANDOM:
            return [], randint(-100000, 100000)
        else:
            return [], self.heuristic.eval_board(self.player1, self.myBoard)
