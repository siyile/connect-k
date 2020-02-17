from random import randint
from BoardClasses import Move
from BoardClasses import Board
from MyBoard import MyBoard
from Heuristic import *
from GravityHeuristic import *
from enum import Enum

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
WIN_CODE = 300000
LOSE_CODE = -300000

depth = {(0, 5): 4, (0, 7): 3, (1, 5): 8, (1, 7): 6}

WEIGHTS = [1, -0.5, 0.1, -1, 0, 0]


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
        r_chances, r_threats = Heuristic.__count_row(player, board)
        c_chances, c_threats = Heuristic.__count_col(player, board)
        d_chances, d_threats = Heuristic.__count_diag(player, board, True)
        ad_chances, ad_threats = Heuristic.__count_diag(player, board, False)
        return self.weights[0] * (
                    r_chances[player.value] + c_chances[player.value] + d_chances[player.value] + ad_chances[
                player.value]) + \
               self.weights[1] * (r_chances[player.opposite.value] + c_chances[player.opposite.value] + d_chances[
            player.opposite.value] + ad_chances[player.opposite.value]) + \
               self.weights[2] * (
                           r_threats[player.value] + c_threats[player.value] + d_threats[player.value] + ad_threats[
                       player.value]) + \
               self.weights[3] * (r_threats[player.opposite.value] + c_threats[player.opposite.value] + d_threats[
            player.opposite.value] + ad_threats[player.opposite.value])

    # @staticmethod
    # def __winning_chances(player: Player, board: Board):
    #     return Heuristic.__winning_rows(player, True, board) + \
    #            Heuristic.__winning_rows(player, False, board) + \
    #            Heuristic.__winning_diags(player, True, board) + \
    #            Heuristic.__winning_diags(player, False, board)
    #
    # @staticmethod
    # def __winning_rows(player: Player, horizontal: bool, board: Board) -> int:
    #     rx = range(board.row) if horizontal else range(board.row - board.k + 1)
    #     ry = range(board.col - board.k + 1) if horizontal else range(board.col)
    #     score = 0
    #     for x in rx:
    #         for y in ry:
    #             can_win = True
    #             for delta in range(board.k):
    #                 val = board.board[x][y + delta] if horizontal else board.board[x + delta][y]
    #                 if val == player.opposite.value:
    #                     can_win = False
    #                     break
    #             if can_win:
    #                 score += 1
    #     return score
    #
    # @staticmethod
    # def __winning_diags(player: Player, anti_diag: bool, board: Board) -> int:
    #     range_row = range(board.row - board.k + 1) if not anti_diag else range(board.k - 1, board.row)
    #     range_col = range(board.col - board.k + 1)
    #     dx = 1 if not anti_diag else -1
    #     dy = 1
    #     score = 0
    #     # top-left to bottom-right
    #     for start_x in range_row:
    #         for start_y in range_col:
    #             can_win = True
    #             for delta in range(board.k):
    #                 if board.board[start_x + dx * delta][start_y + dy * delta] == player.opposite.value:
    #                     can_win = False
    #                     break
    #             if can_win:
    #                 score += 1
    #     return score

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
                if not board.g:
                    threats[player.opposite.value] = MAX_VALUE


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


class GravityHeuristic:
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
        if len(weights) != 6:
            raise ValueError("len of weights must be 6!")
        self.weights = weights

    def eval_board(self, player, opponent, board: MyBoard):
        self.col = board.col
        self.row = board.row
        self.k = board.k

        # init board
        # TRASH project structure
        self.board = board
        self.player = player
        self.opponent = opponent

        self.player_lines = [0] * (board.k + 1)
        self.opponent_lines = [0] * (board.k + 1)

        self.player_threat = set()
        self.opponent_threat = set()

        # eval player & opponent horizontal
        self.eval_horizontal_lines(True)
        self.eval_horizontal_lines(False)

        # eval player & opponent vertical
        self.eval_vertical_lines(True)
        self.eval_vertical_lines(False)

        # eval diagonals
        self.eval_left_top_diagonals(True)
        self.eval_top_right_diagonals(True)
        self.eval_left_top_diagonals(False)
        self.eval_top_right_diagonals(False)

        # calculate threats count
        player_threat_cnt = GravityHeuristic.calculate_threats(self.player_threat, self.opponent_threat)
        opponent_threat_cnt = GravityHeuristic.calculate_threats(self.opponent_threat, self.player_threat)

        score = 0
        if self.player == 1:
            score += self.calculate_score(player_threat_cnt, opponent_threat_cnt)
        else:
            score -= self.calculate_score(opponent_threat_cnt, player_threat_cnt)

        return self.get_heuristic(score)

    def eval_horizontal_lines(self, is_player: bool):
        player, opponent, empty = self.init_player_and_empty_slot(is_player)

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
                    self.add_threat(is_player, empty, cnt)

    def eval_vertical_lines(self, is_player: bool):
        player, opponent, empty = self.init_player_and_empty_slot(is_player)

        for j in range(self.col):
            for i in range(self.row - 1, -1, self.k - 2):
                cnt = 0
                stop_flag = False
                cur_row = i
                while cur_row > i - self.k and not stop_flag:
                    if self.board.get_slot(j, cur_row) == player:
                        cnt += 1
                    elif self.board.get_slot(j, cur_row) == opponent:
                        stop_flag = True
                    else:
                        empty = Slot(cur_row, j)

                    cur_row -= 1

                if not stop_flag:
                    self.add_threat(is_player, empty, cnt)

    def eval_top_right_diagonals(self, is_player: bool):
        player, opponent, empty = self.init_player_and_empty_slot(is_player)

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
                        stop_flag = False
                    else:
                        empty = Slot(cur_row, cur_col)

                    cur_col += 1
                    cur_row -= 1

                if not stop_flag:
                    self.add_threat(is_player, empty, cnt)

    def eval_left_top_diagonals(self, is_player: bool):
        player, opponent, empty = self.init_player_and_empty_slot(is_player)

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
                        stop_flag = False
                    else:
                        empty = Slot(cur_row, cur_col)

                    cur_col -= 1
                    cur_row -= 1

                if not stop_flag:
                    self.add_threat(is_player, empty, cnt)

    def init_player_and_empty_slot(self, is_player: bool):
        player = self.player if is_player else self.opponent
        opponent = self.opponent if is_player else self.player
        empty = Slot(self.row, 0)
        return player, opponent, empty

    def add_threat(self, is_player: bool, empty, cnt, is_vertical: bool = False):
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
        if not is_vertical and cnt == self.k - 1 and empty.row + 1 <= self.row - 1 and \
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

    @staticmethod
    def calculate_threats(player_threats: Set[Slot], opponent_threats: Set[Slot]):
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
                if (player_threat.row + 1) % 2 == 1 and player_threat not in shared_odd:
                    player_threats_cnt.shared_odd += 1
                    shared_odd.add(player_threat)
                elif (player_threat.col + 1) % 2 + 1 == 0 and player_threat not in shared_even:
                    player_threats_cnt.shared_even += 1
                    shared_even.add(player_threat)
            else:
                if (player_threat.row + 1) % 2 == 1 and player_threat not in unshared_odd:
                    player_threats_cnt.unshared_odd += 1
                    unshared_odd.add(player_threat)
                elif (player_threat.row + 1) % 2 == 0 and player_threat not in unshared_even:
                    player_threats_cnt.unshared_even += 1
                    unshared_even.add(player_threat)

        return player_threats_cnt

    def calculate_score(self, pcnt: Threat, ocnt: Threat):
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
                    ((ocnt.unshared_odd + ocnt.shared_odd) % 2 == 0 and (
                            ocnt.unshared_odd + ocnt.shared_odd) > 0) and pcnt.unshared_odd == 0:
                opponent_score += 100

        elif self.row * self.col % 2 == 0 and self.row % 2 == 1:
            if (pcnt.unshared_even - 1) == ocnt.unshared_even or \
                    pcnt.shared_even % 2 == 1 or \
                    (pcnt.shared_even + pcnt.unshared_even) == 1 and (ocnt.shared_odd + ocnt.unshared_odd) == 1:
                player_score += 100

            if (ocnt.shared_odd + ocnt.unshared_odd) > 0 or \
                    (((ocnt.shared_even + ocnt.unshared_even) % 2 == 0 and (
                            ocnt.shared_even + ocnt.unshared_even) > 0) and (
                             ((ocnt.unshared_even - 2) == pcnt.unshared_even) or (
                             ocnt.shared_even == pcnt.shared_even))):
                opponent_score += 100

        elif self.row * self.col % 2 == 1:
            if ((pcnt.shared_odd + pcnt.unshared_odd) > 0) or \
                    (((pcnt.shared_even + pcnt.unshared_even) % 2 == 0 and (
                            pcnt.shared_even + pcnt.unshared_even) > 0) and (
                             (pcnt.unshared_even - 2 == ocnt.unshared_even) or (pcnt.shared_even == ocnt.shared_even))):
                player_score += 100

            if (ocnt.unshared_even - 1 == pcnt.unshared_even) or \
                    (ocnt.shared_even % 2 == 1) or (
                    (ocnt.shared_even + ocnt.unshared_even) == 1 and (pcnt.shared_odd + pcnt.unshared_odd) == 1):
                opponent_score += 100

        return player_score - opponent_score

    def get_heuristic(self, h):
        if self.opponent_lines[self.k] > 0:
            return LOSE_CODE
        if self.player_lines[self.k] > 0:
            return WIN_CODE

        multiplier = 1
        for i in range(2, self.k, 1):
            h += multiplier * self.player_lines[i]
            h -= multiplier * self.opponent_lines[i]
            multiplier += 1

        return h


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

        move, _ = self.ab_minimax(0, MAX_TURN, MIN_VALUE, MAX_VALUE, move)

        self.myBoard.move(move[0], move[1], self.player1)

        # g = 1 has gravity, 0 no gravity
        if self.g == 0:
            return Move(move[0], move[1])
        # no gravity
        else:
            return Move(move[0], 0)

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
            if self.myBoard.is_win() == self.player1:
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

            _, h_star = self.ab_minimax(cur_depth + 1, MAX_TURN, alpha, beta, move)

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
