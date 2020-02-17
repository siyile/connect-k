from MyBoard import MyBoard
from typing import *


MIN_VALUE = -999999
MAX_VALUE = 999999


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
        self.eval_bottom_right_diagonals(True)
        self.eval_top_right_diagonals(True)
        self.eval_bottom_right_diagonals(False)
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
            j = 0
            while j <= self.col - self.k:
                cnt = 0
                stop_flag = False
                cur_col = j
                while cur_col < j + self.k and not stop_flag:
                    if self.board.get_slot(cur_col, i) == player:
                        cnt += 1
                    elif self.board.get_slot(cur_col, i) == opponent:
                        stop_flag = True
                        j = cur_col
                    else:
                        empty = Slot(i, cur_col)

                    cur_col += 1

                if not stop_flag:
                    self.add_threat(is_player, empty, cnt)

                j += 1

    def eval_vertical_lines(self, is_player: bool):
        player, opponent, empty = self.init_player_and_empty_slot(is_player)

        for j in range(self.col):
            i = self.k - 1
            while i - (self.k - 1) >= 0:
                cnt = 0
                stop_flag = False
                cur_row = i
                while cur_row > i - self.k and not stop_flag:
                    if self.board.get_slot(j, cur_row) == player:
                        cnt += 1
                    elif self.board.get_slot(j, cur_row) == opponent:
                        stop_flag = True
                        i = cur_row
                    else:
                        empty = Slot(cur_row, j)

                    cur_row -= 1

                if not stop_flag:
                    self.add_threat(is_player, empty, cnt)

                i -= 1

    def eval_top_right_diagonals(self, is_player: bool):
        player, opponent, empty = self.init_player_and_empty_slot(is_player)

        for i in range(0, 1, self.row - self.k + 1):
            for j in range(0, 1, self.col - self.k + 1):
                cnt = 0
                stop_flag = False
                cur_row = i
                cur_col = j

                while cur_row < i + self.k and cur_col < j + self.k and not stop_flag:
                    if self.board.get_slot(cur_col, cur_row) == player:
                        cnt += 1
                    elif self.board.get_slot(cur_col, cur_row) == opponent:
                        stop_flag = False
                    else:
                        empty = Slot(cur_row, cur_col)

                    cur_col += 1
                    cur_row += 1

                if not stop_flag:
                    self.add_threat(is_player, empty, cnt)

    def eval_bottom_right_diagonals(self, is_player: bool):
        player, opponent, empty = self.init_player_and_empty_slot(is_player)

        for i in range(0, 1, self.row - self.k + 1):
            for j in range(self.k - 1, 1, self.col):
                cnt = 0
                stop_flag = False
                cur_row = i
                cur_col = j

                while cur_row < i + self.k and cur_col >= j - self.k + 1 and not stop_flag:
                    if self.board.get_slot(cur_col, cur_row) == player:
                        cnt += 1
                    elif self.board.get_slot(cur_col, cur_row) == opponent:
                        stop_flag = False
                    else:
                        empty = Slot(cur_row, cur_col)

                    cur_col -= 1
                    cur_row += 1

                if not stop_flag:
                    self.add_threat(is_player, empty, cnt)

    def init_player_and_empty_slot(self, is_player: bool):
        player = self.player if is_player else self.opponent
        opponent = self.opponent if is_player else self.player
        empty = Slot(0, 0)
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
                if player_threat.col == opponent_threat.col and player_threat.row >= opponent_threat.row:
                    shared = True
                    break

            if shared:
                if (player_threat.row + 1) % 2 == 1 and player_threat not in shared_odd:
                    player_threats_cnt.shared_odd += 1
                    shared_odd.add(player_threat)
                elif player_threat.col % 2 == 0 and player_threat not in shared_even:
                    player_threats_cnt.shared_even += 1
                    shared_even.add(player_threat)
            else:
                if (player_threat.row + 1) % 2 == 1 and player_threat not in unshared_odd:
                    player_threats_cnt.unshared_odd += 1
                    unshared_odd.add(player_threat)
                elif player_threat.row % 2 == 0 and player_threat not in unshared_even:
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
                    ((ocnt.unshared_odd + ocnt.shared_odd) % 2 == 0 and (ocnt.unshared_odd + ocnt.shared_odd) > 0) and pcnt.unshared_odd == 0:
                opponent_score += 100

        elif self.row * self.col % 2 == 0 and self.row % 2 == 1:
            if (pcnt.unshared_even - 1) == ocnt.unshared_even or \
                    pcnt.shared_even % 2 == 1 or \
                    (pcnt.shared_even + pcnt.unshared_even) == 1 and (ocnt.shared_odd + ocnt.unshared_odd) == 1:
                player_score += 100

            if (ocnt.shared_odd + ocnt.unshared_odd) > 0 or \
                    (((ocnt.shared_even + ocnt.unshared_even) % 2 == 0 and (ocnt.shared_even + ocnt.unshared_even) > 0) and (((ocnt.unshared_even - 2) == pcnt.unshared_even) or (ocnt.shared_even == pcnt.shared_even))):
                opponent_score += 100

        elif self.row * self.col % 2 == 1:
            if ((pcnt.shared_odd + pcnt.unshared_odd) > 0) or \
                    (((pcnt.shared_even + pcnt.unshared_even) % 2 == 0 and (pcnt.shared_even + pcnt.unshared_even) > 0) and ((pcnt.unshared_even - 2 == ocnt.unshared_even) or (pcnt.shared_even == ocnt.shared_even))):
                player_score += 100

            if (ocnt.unshared_even - 1 == pcnt.unshared_even) or \
                    (ocnt.shared_even % 2 == 1) or ((ocnt.shared_even + ocnt.unshared_even) == 1 and (pcnt.shared_odd + pcnt.unshared_odd) == 1):
                opponent_score += 100

        return player_score - opponent_score

    def get_heuristic(self, h):
        if self.opponent_lines[self.k] > 0:
            return MIN_VALUE
        if self.player_lines[self.k] > 0:
            return MAX_VALUE

        multiplier = 1
        for i in range(2, self.k, 1):
            h += multiplier * self.player_lines[i]
            h -= multiplier * self.opponent_lines[i]
            multiplier += 1

        return h


