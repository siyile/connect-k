from typing import *
from MyBoard import *
from abc import *

MAX_VALUE = 99999
WIN_CODE = 300000
LOSE_CODE = -300000


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