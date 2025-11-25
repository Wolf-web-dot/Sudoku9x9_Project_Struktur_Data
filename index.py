import pygame
import random

pygame.init()

# ----------------------------
# Node mewakili 1 sel dengan history
# ----------------------------
class Node:
    def __init__(self):
        self.value = 0
        self.fixed = False
        self.valid = True
        self.history = []  # menyimpan nilai sebelumnya

# ----------------------------
# Grid 9x9
# ----------------------------
class SudokuGrid:
    def __init__(self):
        self.size = 9
        self.grid = [[Node() for _ in range(9)] for _ in range(9)]

    def get(self, r, c):
        return self.grid[r][c]

    def row(self, r):
        return [n.value for n in self.grid[r]]

    def col(self, c):
        return [self.grid[i][c].value for i in range(9)]

    def subgrid(self, r, c):
        sr, sc = (r // 3) * 3, (c // 3) * 3
        return [self.grid[i][j].value for i in range(sr, sr+3) for j in range(sc, sc+3)]

# ----------------------------
# Sudoku Board + Logic + History
# ----------------------------
class SudokuBoard:
    def __init__(self):
        self.grid = SudokuGrid()

    def can_place(self, r, c, value):
        if value in self.grid.row(r):
            return False
        if value in self.grid.col(c):
            return False
        if value in self.grid.subgrid(r, c):
            return False
        return True

    # memasukkan angka, tetap ditaruh tapi validitas disimpan
    def place_number(self, r, c, value):
        node = self.grid.get(r, c)
        if node.fixed:
            return False
        node.history.append(node.value)  # simpan nilai lama
        node.value = value
        node.valid = self.can_place(r, c, value)  # merah jika invalid
        return True

    # undo per sel
    def undo_cell(self, r, c):
        node = self.grid.get(r, c)
        if node.history:
            node.value = node.history.pop()
            node.valid = True

    # isi angka random fixed
    def fill_random_cells(self, count=25):
        attempts = 0
        filled = 0
        while filled < count and attempts < 500:
            attempts += 1
            r = random.randint(0, 8)
            c = random.randint(0, 8)
            node = self.grid.get(r, c)
            if node.value != 0:
                continue
            value = random.randint(1, 9)
            if self.can_place(r, c, value):
                node.value = value
                node.fixed = True
                filled += 1

    # cek semua sel valid / tidak
    def check_validity(self):
        for r in range(9):
            for c in range(9):
                node = self.grid.get(r, c)
                if node.value == 0:
                    node.valid = True
                    continue
                node.valid = self.can_place_for_check(r, c, node.value)

    def can_place_for_check(self, r, c, value):
        row = self.grid.row(r)
        col = self.grid.col(c)
        sub = self.grid.subgrid(r, c)
        if row.count(value) > 1:
            return False
        if col.count(value) > 1:
            return False
        if sub.count(value) > 1:
            return False
        return True

    def reset(self):
        self.__init__()

    # fungsi untuk debug: print history semua sel
    def print_history(self):
        for r in range(9):
            for c in range(9):
                node = self.grid.get(r, c)
                if node.history:
                    print(f"({r},{c}): {node.history}")

# ----------------------------
# UI Setup
# ----------------------------
WIDTH, HEIGHT = 540, 600
CELL = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku with Undo & Delete")
FONT = pygame.font.Font(None, 40)
BIG = pygame.font.Font(None, 60)

# ----------------------------
# Draw Grid
# ----------------------------
def draw_grid(board, selected, message, flash_until):
    screen.fill((255, 255, 255))
    for r in range(9):
        for c in range(9):
            x, y = c * CELL, r * CELL
            rect = pygame.Rect(x, y, CELL, CELL)
            # highlight selected
            if selected == (r, c):
                pygame.draw.rect(screen, (200, 230, 255), rect)
            node = board.grid.get(r, c)
            if node.value != 0:
                if pygame.time.get_ticks() < flash_until:
                    color = (255, 0, 0)
                else:
                    if node.fixed:
                        color = (0, 0, 0)  # fixed hitam
                    else:
                        color = (255, 0, 0) if not node.valid else (0, 0, 200)  # merah jika invalid
                text = BIG.render(str(node.value), True, color)
                screen.blit(text, (x + 18, y + 10))
            pygame.draw.rect(screen, (150, 150, 150), rect, 1)
    # garis tebal 3x3
    for i in range(10):
        w = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, (0, 0, 0), (i * CELL, 0), (i * CELL, 540), w)
        pygame.draw.line(screen, (0, 0, 0), (0, i * CELL), (540, i * CELL), w)
    # message
    msg = FONT.render(message, True, (255, 0, 0))
    screen.blit(msg, (10, 550))
    pygame.display.flip()

# ----------------------------
# Main Loop
# ----------------------------
def main():
    board = SudokuBoard()
    selected = None
    message = ""
    flash_until = 0

    board.fill_random_cells(25)

    running = True
    clock = pygame.time.Clock()

    while running:
        draw_grid(board, selected, message, flash_until)
        message = ""

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if mx < 540 and my < 540:
                    selected = (my // CELL, mx // CELL)
            elif e.type == pygame.KEYDOWN:
                if selected:
                    r, c = selected
                    # angka 1-9
                    if pygame.K_1 <= e.key <= pygame.K_9:
                        val = e.key - pygame.K_0
                        board.place_number(r, c, val)
                        board.check_validity()
                    # undo dengan U
                    elif e.key == pygame.K_u:
                        node = board.grid.get(r, c)
                        if not node.fixed:
                            board.undo_cell(r, c)
                    # delete / backspace mengosongkan sel
                    elif e.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        node = board.grid.get(r, c)
                        if not node.fixed:
                            node.history.append(node.value)
                            node.value = 0
                            node.valid = True
                    # reset board
                    elif e.key == pygame.K_r:
                        board.reset()
                        board.fill_random_cells(25)
                    # debug: print history
                    elif e.key == pygame.K_h:
                        board.print_history()

        clock.tick(30)
    pygame.quit()

# Run Program
if __name__ == "__main__":
    main()
