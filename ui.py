import pygame
from pygame.locals import *
from coba import SudokuBoard   # IMPORT LOGIC KAMU

WIDTH = 540
HEIGHT = 540
CELL = WIDTH // 9

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku - Pygame")

font = pygame.font.Font(None, 48)

# Panggil logic sudoku kamu
board = SudokuBoard()


def draw_grid():
    for i in range(10):
        thick = 4 if i % 3 == 0 else 1
        pygame.draw.line(win, (0, 0, 0), (0, i*CELL), (WIDTH, i*CELL), thick)
        pygame.draw.line(win, (0, 0, 0), (i*CELL, 0), (i*CELL, HEIGHT), thick)


def draw_numbers():
    for r in range(9):
        for c in range(9):
            value = board.grid.get(r, c).value
            if value != 0:
                num = font.render(str(value), True, (0, 0, 0))
                win.blit(num, (c*CELL + 18, r*CELL + 10))


def highlight_cell(r, c):
    pygame.draw.rect(win, (200, 220, 255), (c*CELL, r*CELL, CELL, CELL))


def main():
    selected = None
    running = True

    while running:
        win.fill((255, 255, 255))

        # highlight selected
        if selected:
            highlight_cell(selected[0], selected[1])

        draw_grid()
        draw_numbers()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # pilih cell
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                c = x // CELL
                r = y // CELL
                selected = (r, c)

            # input angka ke LinkedList
            if event.type == KEYDOWN:
                if selected and event.unicode.isdigit():
                    num = int(event.unicode)
                    if 1 <= num <= 9:
                        r, c = selected
                        success = board.set_value(r, c, num)
                        
                        if not success:
                            print("Invalid move")

                # Undo
                if event.key == pygame.K_u:
                    board.undo()

                # Clear selected
                if event.key == pygame.K_BACKSPACE:
                    r, c = selected
                    board.set_value(r, c, 0)

        pygame.display.update()

    pygame.quit()


main()