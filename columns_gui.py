# Steven Rivera
# ID: 69434439

import pygame
import columns_model

_BACKGROUND_COLOR = pygame.Color(0, 0, 0)
INITIAL_SIZE = (420, 910)
FRAME_RATE = 30
TICK = 20
COLORS = {'R': pygame.Color(255, 0, 0),
          'G': pygame.Color(0, 255, 0),
          'B': pygame.Color(0, 0, 255),
          'Y': pygame.Color(255, 255, 0),
          'P': pygame.Color(149, 0, 255),
          'O': pygame.Color(255, 123, 0),
          'C': pygame.Color(0, 255, 255)
          }


class ColumnsGame:
    def __init__(self):
        self._clock = pygame.time.Clock()
        self._running = True
        self._game_state = columns_model.GameState()
        self._time = 0
        

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption('Columns Game')
        self._resize_surface(INITIAL_SIZE)

        while self._running:
            self._clock.tick(FRAME_RATE)
            self._handle_game()
            self._handle_events()
            self._time_passing()
            self._draw_frame()
            self._check_for_matches()

        pygame.quit()


    def _handle_game(self):
        if self._game_state.gameover is True:
            self._end_game()
        else:
            if self._game_state.faller() is None:
                self._game_state.create_new_faller()
                while self._game_state._is_column_full():
                    self._game_state.create_new_faller()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._end_game()
            if event.type == pygame.VIDEORESIZE:
                self._resize_surface(event.size)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._game_state.rotate_faller()
                elif event.key == pygame.K_RIGHT:
                    try:
                        self._game_state.shift('>')
                    except columns_model.InvalidMoveError:
                        pass
                elif event.key == pygame.K_LEFT:
                    try:
                        self._game_state.shift('<')
                    except columns_model.InvalidMoveError:
                        pass
                elif event.key == pygame.K_DOWN:
                    if self._game_state.faller() is not None:
                        if not self._game_state.faller().landed:
                            self._increment_faller()
                            self._time = 0
                
    def _check_for_matches(self):
        if self._game_state.faller() is None:
            matches = columns_model.CheckForMatches(self._game_state)
            indexes_of_matches = matches.matches_indexes()

            if len(indexes_of_matches) != 0:
                self._animate_matches(indexes_of_matches)
                self._game_state.clear_board_of_matches(indexes_of_matches)
                self._game_state.gravity()
                self._draw_frame()

                if self._game_state.gameover:
                    self._game_state.gameover = False
                    self._game_state.gravity(self._old_faller)
                    self._game_state._faller = self._old_faller
                    self._game_state.faller().increment_row()

                    if columns_model.NONE in self._game_state.board[self._game_state.faller().column_index]:
                        self._game_state.faller().increment_row()
                
                self._check_for_matches()
        

    def _animate_matches(self, indexes_of_matches):
        for column_index, row_index in indexes_of_matches:
            color = pygame.Color(255, 255, 255)

            frac_x = column_index * (1 / 6)
            frac_y = row_index * (1 / 13)

            pixel_x = int(frac_x * self._surface.get_width())
            pixel_y = int(frac_y * self._surface.get_height())

            pixel_width = int(columns_model.jewel_width() * self._surface.get_width())
            pixel_height = int(columns_model.jewel_height() * self._surface.get_height())

            player_rect = pygame.Rect(pixel_x, pixel_y, pixel_width, pixel_height)
            pygame.draw.rect(self._surface, color, player_rect)

        pygame.display.flip()
        self._clock.tick(2)

    def _time_passing(self):
        if self._time == TICK:
            self._time = 0
            self._increment_faller()
        else:       
            self._time += 1

    def _increment_faller(self):
        if self._game_state.faller() is not None:
            try:
                self._game_state.drop_faller_one_row()
            except columns_model.FallerHasAlreadyLandedError:
                self._old_faller = self._game_state.faller()
                self._game_state.freeze_faller()
                    
        

    def _draw_frame(self):
        self._surface.fill(_BACKGROUND_COLOR)
        self._draw_grid()
        self._draw_board()
        pygame.display.flip()

    def _draw_grid(self):
        frac_x = 1 / 6
        frac_y = 1

        for _ in range(5):
            pixel_x = frac_x * self._surface.get_width()
            pixel_y = frac_y * self._surface.get_height()
            pygame.draw.line(self._surface, (255, 255, 255), (int(pixel_x), 0), (int(pixel_x), int(pixel_y)))
            frac_x += 1 / 6

        frac_x = 1
        frac_y = 1 / 13
        for _ in range(12):
            pixel_x = frac_x * self._surface.get_width()
            pixel_y = frac_y * self._surface.get_height()
            pygame.draw.line(self._surface, (255, 255, 255), (0, int(pixel_y)), (int(pixel_x), int(pixel_y)))
            frac_y += 1 / 13

    def _draw_board(self):
        for row_index in range(self._game_state.num_rows):
            for column_index, column in enumerate(self._game_state.board):
                jewel = column[row_index]

                if jewel == columns_model.NONE:
                    pass
                else:
                    color = COLORS[jewel]

                    frac_x = column_index * (1 / 6)
                    frac_y = row_index * (1 / 13)

                    pixel_x = int(frac_x * self._surface.get_width())
                    pixel_y = int(frac_y * self._surface.get_height())

                    pixel_width = int(columns_model.jewel_width() * self._surface.get_width())
                    pixel_height = int(columns_model.jewel_height() * self._surface.get_height())

                    player_rect = pygame.Rect(pixel_x, pixel_y, pixel_width, pixel_height)
                    pygame.draw.rect(self._surface, color, player_rect)

    def _resize_surface(self, size: (int, int)) -> None:
        self._surface = pygame.display.set_mode(size, pygame.RESIZABLE)

    def _end_game(self) -> None:
        self._running = False


if __name__ == '__main__':
    ColumnsGame().run()
