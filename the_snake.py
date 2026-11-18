"""Игра «Змейка», реализованная с помощью Pygame."""

from random import choice

import pygame

# Размеры игрового поля и одной клетки.
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Клетки игрового поля рассчитываются теперь только один раз.
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

# Направления движения.
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Разрешённые направления для текущего направления и нажатой клавиши.
DIRECTION_BY_KEY = {
    (UP, pygame.K_LEFT): LEFT,
    (UP, pygame.K_RIGHT): RIGHT,
    (DOWN, pygame.K_LEFT): LEFT,
    (DOWN, pygame.K_RIGHT): RIGHT,
    (LEFT, pygame.K_UP): UP,
    (LEFT, pygame.K_DOWN): DOWN,
    (RIGHT, pygame.K_UP): UP,
    (RIGHT, pygame.K_DOWN): DOWN,
}

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 10

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для объектов игрового поля."""

    def __init__(self, position=SCREEN_CENTER, body_color=None):
        """Сохраняет позицию и цвет игрового объекта."""
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Рисует одну клетку заданным цветом или цветом объекта."""
        if not color:
            color = self.body_color

        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        if color != BOARD_BACKGROUND_COLOR:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Ожидает реализации отрисовки в дочернем классе."""
        raise NotImplementedError(
            'Метод draw() должен быть реализован в дочернем классе.'
        )


class Apple(GameObject):
    """Яблоко, которое появляется в свободной клетке поля."""

    def __init__(
        self, position=SCREEN_CENTER, body_color=APPLE_COLOR,
        occupied_positions=None
    ):
        """Создаёт яблоко, учитывая занятые змейкой клетки."""
        super().__init__(position, body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Выбирает случайную клетку, не занятую змейкой."""
        occupied = set(occupied_positions or ())
        free_cells = ALL_CELLS - occupied

        if not free_cells:
            raise ValueError('На игровом поле нет свободных клеток.')

        self.position = choice(tuple(free_cells))

    def draw(self):
        """Отрисовывает яблоко."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка, перемещающаяся по игровому полю."""

    def __init__(self, position=SCREEN_CENTER, body_color=SNAKE_COLOR):
        """Создаёт змейку и задаёт направление первого движения вправо."""
        super().__init__(position, body_color)
        self.reset(first_start=True)

    def reset(self, first_start=False):
        """Сбрасывает змейку, выбирая случайное направление при рестарте."""
        self.positions = [self.position]
        self.direction = RIGHT if first_start else choice(DIRECTIONS)
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Применяет направление, выбранное игроком."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает голову на клетку и сохраняет старый хвост."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        new_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        self.positions.insert(0, (new_x, new_y))
        self.last = self.positions.pop()

    def grow(self):
        """Возвращает хвост после съеденного яблока, удлиняя змейку."""
        self.positions.append(self.last)
        self.last = None

    def draw(self):
        """Стирает предыдущий хвост и рисует новую голову."""
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)
        self.draw_cell(self.get_head_position())


def handle_keys(game_object):
    """Обрабатывает закрытие окна и изменение направления змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

            new_direction = DIRECTION_BY_KEY.get(
                (game_object.direction, event.key)
            )
            if new_direction is not None:
                game_object.next_direction = new_direction


def main():
    """Запускает игру и проверяет события каждого игрового шага."""
    pygame.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    apple.draw()
    pygame.display.update()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            if apple.position in snake.positions:
                apple.randomize_position(snake.positions)

        elif snake.get_head_position() == apple.position:
            snake.grow()
            if len(snake.positions) == len(ALL_CELLS):
                pygame.quit()
                return
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
