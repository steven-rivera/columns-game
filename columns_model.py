# Steven Rivera
# ID: 69434439

import random

NONE = 0
_PLAYER_WIDTH = 1 / 6
_PLAYER_HEIGHT = 1 / 13

COLORS = {1: 'R', 2: 'B', 3: 'G', 4: 'Y', 5: 'P', 6: 'O', 7: 'C'}


class InvalidMoveError(Exception):
    pass


class FallerHasNotLandedError(Exception):
    pass


class FallerHasAlreadyLandedError(Exception):
    pass


class FallerIsFrozenError(Exception):
    pass


class Faller:
    def __init__(self, column: int, top: str, middle: str, bottom: str):
        self.column_index = column - 1
        self._jewels = [top, middle, bottom]
        self.row_positions = [-3, -2, -1]
        self.index = 0
        self.landed = False
        self.frozen = False

    def increment_row(self):
        """Shifts the row positions of the faller by one."""
        for index in range(3):
            self.row_positions[index] += 1

    def rotate(self):
        """Rotates the jewel."""
        self._jewels = self._jewels[-1:] + self._jewels[:-1]

    def width(self):
        return _PLAYER_WIDTH

    def height(self):
        return _PLAYER_HEIGHT

    def jewels(self):
        return self._jewels

    def land(self):
        self.landed = True

    def freeze(self):
        self.frozen = True


class GameState:
    def __init__(self):
        self.num_rows = 13
        self.num_columns = 6
        self.board = _create_empty_board()
        self._faller = None
        self.gameover = False

    def faller(self):
        return self._faller

    def end_game(self):
        """Ends the game."""
        self.gameover = True

    def save(self):
        self.gameover = False

    def create_new_faller(self):
        """Creates a new faller in the given columns with the given colored jewels."""
        column = _genrate_random_column()
        top, middle, bottom = _generate_random_colors()

        self._faller = Faller(column, top, middle, bottom)

    def drop_faller_one_row(self):
        """Drops the faller one row. If the faller has landed an exception is raised."""
        if not self._faller.landed:
            if self._is_column_full():
                self.end_game()
            else:
                self._faller.increment_row()
                self._update_board()
        else:
            raise FallerHasAlreadyLandedError

    def freeze_faller(self):
        """Freezes the faller and ends the game if faller doesn't fit.
        If faller hasn't landed exception is raised."""
        if self._faller.landed:
            self._faller.freeze()
            self._is_game_over()
            self._faller = None
        else:
            raise FallerHasNotLandedError

    def rotate_faller(self):
        """Rotates the faller and updates the board to reflect the rotation."""
        self._faller.rotate()
        self._update_board()

    def shift(self, symbol: str):
        """Shifts the faller left or right if faller is not frozen and there are
        no pieces blocking the shift, else an eception is raised."""
        if self._faller.frozen:
            raise FallerIsFrozenError

        self._is_shift_valid(symbol)
        self._clear_prior_faller_column()

        if symbol == '>':
            self._faller.column_index += 1

        elif symbol == '<':
            self._faller.column_index -= 1

        self._update_board()

    def gravity(self, old_faller=None):
        """When jewels are popped this fuction shifts all the pieces down acting
        like gravity."""
        for index, column in enumerate(self.board):
            new_column = [jewel for jewel in column if jewel != NONE]

            if old_faller is not None:
                if old_faller.column_index == index:
                    old_faller.row_positions = old_faller.row_positions[::-1]
                    old_faller._jewels = old_faller.jewels()[::-1]

                    for jewel_index, row_index in enumerate(old_faller.row_positions):
                        if row_index < 0:
                            if len(new_column) < self.num_rows:
                                new_column.insert(0, old_faller.jewels()[jewel_index])
                            else:
                                pass

            for _ in range(self.num_rows - len(new_column)):
                new_column.insert(0, NONE)

            self.board[index] = new_column

    def clear_board_of_matches(self, indexes_of_matches: list[tuple[int, int]]):
        """Given the indexes of the jewels that have matches this function clears
        the jewels from the board."""
        for column_index, row_index in indexes_of_matches:
            self.board[column_index][row_index] = NONE

    def _is_shift_valid(self, symbol: str):
        if symbol == '>':
            if self._faller.column_index + 1 > self.num_columns - 1:
                raise InvalidMoveError

            for index, row_position in enumerate(self._faller.row_positions):
                if row_position < 0:
                    pass
                else:
                    if self.board[self._faller.column_index + 1][row_position] != NONE:
                        raise InvalidMoveError

        elif symbol == '<':
            if self._faller.column_index - 1 < 0:
                raise InvalidMoveError

            for index, row_position in enumerate(self._faller.row_positions):
                if row_position < 0:
                    pass
                else:
                    if self.board[self._faller.column_index - 1][row_position] != NONE:
                        raise InvalidMoveError

    def _update_board(self):
        for index, row_position in enumerate(self._faller.row_positions):
            if row_position < 0:
                pass
            else:
                self.board[self._faller.column_index][row_position] = self._faller.jewels()[index]
                if index == 0 and row_position > 0:
                    self.board[self._faller.column_index][row_position - 1] = NONE

        if self._has_faller_landed():
            self._faller.land()

        if self._faller.landed and not self._has_faller_landed():
            self._faller.landed = False

    def _is_game_over(self):
        for row_index in self._faller.row_positions:
            if row_index < 0:
                self.end_game()

    def _is_column_full(self):
        if NONE in self.board[self._faller.column_index]:
            return False
        else:
            return True

    def _clear_prior_faller_column(self):
        for row_position in self._faller.row_positions:
            if row_position < 0:
                pass
            else:
                self.board[self._faller.column_index][row_position] = NONE

    def _has_faller_landed(self) -> bool:
        if self._faller.row_positions[-1] == self.num_rows - 1:
            return True
        if self.board[self._faller.column_index][self._faller.row_positions[-1] + 1] != NONE:
            return True

        return False


class CheckForMatches:
    def __init__(self, game: GameState):
        self.board = game.board
        self.num_columns = game.num_columns
        self.num_rows = game.num_rows
        self.matching_indexes = set()

    def matches_indexes(self) -> set[tuple[int, int]]:
        """Returns a set of tuples that each contain the column and row index
        of all the jewels that have matches. An empty set is return if there are
        no matches."""
        for col in range(self.num_columns):
            for row in range(self.num_rows):
                if self.board[col][row] == NONE or (col, row) in self.matching_indexes:
                    pass
                else:
                    self._matches_begining_at(col, row)

        return self.matching_indexes

    def _matches_begining_at(self, col: int, row: int):
        column_and_row_deltas = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        for coldelta, rowdelta in column_and_row_deltas:
            self._any_matches(coldelta, rowdelta, col, row)

    def _any_matches(self, coldelta: int, rowdelta: int, col: int, row: int):
        jewel = self.board[col][row]
        possible_match = True
        indexes = {(col, row)}

        i = 1
        while possible_match:
            if self._is_valid_column_number(col + coldelta * i) \
                    and self._is_valid_row_number(row + rowdelta * i) \
                    and self.board[col + coldelta * i][row + rowdelta * i] == jewel:
                indexes.add((col + coldelta * i, row + rowdelta * i))
                i += 1
            else:
                possible_match = False
                if len(indexes) >= 3:
                    self.matching_indexes.update(indexes)

    def _is_valid_column_number(self, column_number) -> bool:
        """Returns True if the given column number is valid; returns False otherwise"""
        return 0 <= column_number < self.num_columns

    def _is_valid_row_number(self, row_number) -> bool:
        """Returns True if the given row number is valid; returns False otherwise"""
        return 0 <= row_number < self.num_rows


def _create_empty_board() -> list[list[int]]:
    """
    Creates a new game board.  Initially, a game board has the size
    13 x 6 and is comprised only of integers with the
    value NONE
    """
    board = []

    for col in range(6):
        board.append([])
        for row in range(13):
            board[-1].append(NONE)

    return board


def _generate_random_colors():
    colors = []

    for _ in range(3):
        color = COLORS[random.randint(1, 7)]
        colors.append(color)

    return colors


def _genrate_random_column():
    return random.randint(1, 6)


def jewel_width():
    return _PLAYER_WIDTH


def jewel_height():
    return _PLAYER_HEIGHT
