class Node:
    def __init__(self, value=0, fixed=False):
        self.value = value
        self.fixed = fixed
        self.history = []
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        prev = None
        for _ in range(81):
            node = Node()
            if self.head is None:
                self.head = node
            else:
                prev.next = node
            prev = node

    def get_node(self, row, col):
        idx = row * 9 + col
        cur = self.head
        for _ in range(idx):
            cur = cur.next
        return cur


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
        cur = self.grid.head
        vals = []
        row = []
        for i in range(81):
            row.append(cur.value)
            if len(row) == 9:
                vals.append(row)
                row = []
            cur = cur.next
        return vals

    def is_valid_move(self, row, col, value):
        if value == 0:
            return True

        for c in range(9):
            n = self.grid.get_node(row, c)
            if c != col and n.value == value:
                return False

        for r in range(9):
            n = self.grid.get_node(r, col)
            if r != row and n.value == value:
                return False

        sr = (row // 3) * 3
        sc = (col // 3) * 3
        for r in range(sr, sr + 3):
            for c in range(sc, sc + 3):
                n = self.grid.get_node(r, c)
                if (r != row or c != col) and n.value == value:
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
        node = self.grid.get_node(row, col)
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
        node = self.grid.get_node(r, c)
        node.value = old_value
        return True

    def load_puzzle(self, puzzle):
        cur = self.grid.head
        for r in range(9):
            for c in range(9):
                v = puzzle[r][c]
                cur.value = v
                cur.fixed = (v != 0)
                cur.history = []
                cur = cur.next

    def reset(self):
        cur = self.grid.head
        for _ in range(81):
            cur.value = 0
            cur.fixed = False
            cur.history = []
            cur = cur.next
        self.undo = UndoStack()
