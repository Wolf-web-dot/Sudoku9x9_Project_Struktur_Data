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

    # ---------- helpers ----------
    def board_values(self):
        """Return current board as 9x9 list of ints."""
        return [[self.grid.get(r, c).value for c in range(9)] for r in range(9)]

    # ---------- local validation ----------
    def is_valid_move(self, row, col, value):
        """Check row/col/3x3 duplicates ignoring (row,col) itself."""
        if value == 0:
            return True

        # row
        for c in range(9):
            if c != col and self.grid.get(row, c).value == value:
                return False

        # col
        for r in range(9):
            if r != row and self.grid.get(r, col).value == value:
                return False

        # subgrid
        sr = (row // 3) * 3
        sc = (col // 3) * 3
        for r in range(sr, sr + 3):
            for c in range(sc, sc + 3):
                if (r != row or c != col) and self.grid.get(r, c).value == value:
                    return False

        return True

    # ---------- solver on a board copy (no deep copy module) ----------
    def _can_place_on_board(self, board, row, col, value):
        # row
        for c in range(9):
            if board[row][c] == value:
                return False
        # col
        for r in range(9):
            if board[r][col] == value:
                return False
        # subgrid
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
        """Simulate placing value on a copy of board and try solving."""
        # build board copy
        board = self.board_values()
        board[row][col] = value
        # quick check: if violates immediate constraints on the copy, unsolvable
        # (this duplicates is_valid_move but on board copy - helpful for safety)
        # Now run solver
        return self._solve_board(board)

    # ---------- set / undo with solvability check ----------
    def set_value(self, row, col, value):
        node = self.grid.get(row, col)

        # angka fixed tidak boleh dirubah
        if node.fixed:
            return False, "fixed"

        old = node.value

        # Tetap ijinkan input 0 (hapus angka)
        if value == 0:
            node.history.append((old, value, "clear"))
            node.value = 0
            return True, "ok"

        # Cek validasi sudoku (baris, kolom, blok)
        valid = self.is_valid_move(row, col, value)
        solvable = self.is_solvable_after_move(row, col, value)

        # Simpan nilai apapun, tapi historynya diberi label
        if not valid or not solvable:
            node.history.append((old, value, "invalid"))
            node.value = value
            return True, "invalid"

        # Jika semua OK
        node.history.append((old, value, "ok"))
        node.value = value
        return True, "ok"



    def undo_last(self):
        action = self.undo.pop()
        if action is None:
            return False
        r, c, old_value, new_value = action
        self.grid.set(r, c, old_value)
        return True

    # ---------- load/reset ----------
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
