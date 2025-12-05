class Node:
    def __init__(self, row, col, value=0, fixed=False):
        self.row = row
        self.col = col
        self.value = value
        self.fixed = fixed
        self.history = []
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.index = {}
        prev = None
        for r in range(9):
            for c in range(9):
                node = Node(r, c)
                self.index[(r, c)] = node
                if self.head is None:
                    self.head = node
                else:
                    prev.next = node
                prev = node

    def get(self, row, col):
        return self.index[(row, col)]

    def set(self, row, col, value):
        node = self.index[(row, col)]
        node.history.append(node.value)
        node.value = value

class UndoStack:
    def __init__(self):
        self.stack = []

    def push(self, row, col, old_value, new_value):
        self.stack.append((row, col, old_value, new_value))

    def pop(self):
        if not self.stack:
            return None
        return self.stack.pop()

class Sudoku:
    def __init__(self):
        self.grid = LinkedList()
        self.undo = UndoStack()

    def board_values(self):
        return [[self.grid.get(r, c).value for c in range(9)] for r in range(9)]

    def is_valid_move(self, row, col, value):
        if value == 0:
            return True
        for c in range(9):
            if c != col and self.grid.get(row, c).value == value:
                return False
        for r in range(9):
            if r != row and self.grid.get(r, col).value == value:
                return False
        sr = (row // 3) * 3
        sc = (col // 3) * 3
        for r in range(sr, sr + 3):
            for c in range(sc, sc + 3):
                if (r != row or c != col) and self.grid.get(r, c).value == value:
                    return False
        return True

    def _can_place_on_board(self, board, row, col, value):
        for c in range(9):
            if board[row][c] == value:
                return False
        for r in range(9):
            if board[r][col] == value:
                return False
        sr = (row // 3) * 3
        sc = (col // 3) * 3
        for r in range(sr, sr + 3):
            for c in range(sc, sc + 3):
                if board[r][c] == value:
                    return False
        return True

    def _find_empty_on_board(self, board):
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return r, c
        return None

    def _solve_board(self, board):
        pos = self._find_empty_on_board(board)
        if not pos:
            return True
        r, c = pos
        for n in range(1, 10):
            if self._can_place_on_board(board, r, c, n):
                board[r][c] = n
                if self._solve_board(board):
                    return True
                board[r][c] = 0
        return False

    def is_solvable_after_move(self, row, col, value):
        board = self.board_values()
        board[row][col] = value
        return self._solve_board(board)

    def set_value(self, row, col, value):
        node = self.grid.get(row, col)
        if node.fixed:
            return False, "fixed"
        old = node.value
        if value == 0:
            node.history.append((old, value, "clear"))
            node.value = 0
            self.undo.push(row, col, old, value)
            return True, "ok"
        valid = self.is_valid_move(row, col, value)
        solvable = self.is_solvable_after_move(row, col, value)
        if not valid or not solvable:
            node.history.append((old, value, "invalid"))
            node.value = value
            self.undo.push(row, col, old, value)
            return True, "invalid"
        node.history.append((old, value, "ok"))
        node.value = value
        self.undo.push(row, col, old, value)
        return True, "ok"

    def undo_last(self):
        action = self.undo.pop()
        if action is None:
            return False
        r, c, old_value, new_value = action
        node = self.grid.get(r, c)
        node.value = old_value
        return True

    def load_puzzle(self, puzzle):
        for r in range(9):
            for c in range(9):
                v = puzzle[r][c]
                node = self.grid.get(r, c)
                node.value = v
                node.fixed = (v != 0)

    def reset(self):
        for r in range(9):
            for c in range(9):
                node = self.grid.get(r, c)
                node.value = 0
                node.fixed = False
        self.undo = UndoStack()
