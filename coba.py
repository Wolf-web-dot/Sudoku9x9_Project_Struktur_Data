from tkinter import messagebox


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

    def print_board(self):
        cur = self.head
        for r in range(9):
            row = []
            for c in range(9):
                row.append(cur.value)
                cur = cur.next
            print(row)
        print("-" * 30)

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

    def board_values(self): # Returns the current board as a 2D list
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

    def is_valid_move(self, row, col, value): # Check if placing value at (row, col) is valid
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

    def _can_place_on_board(self, board, row, col, value): # Helper for solving
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

    def _find_empty_on_board(self, board): # Helper for solving
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return r, c
        return None

    def _solve_board(self, board): # Backtracking solver
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

    def is_solvable_after_move(self, row, col, value): # Check if board is solvable after placing value at (row, col)
        board = self.board_values()
        board[row][col] = value
        return self._solve_board(board)

    def set_value(self, row, col, value): # Set value at (row, col) with validation and undo support
        node = self.grid.get_node(row, col)
        if node.fixed:
            return False, "fixed"

        for old_v, new_v, status in node.history:
            if new_v == value and value != 0 and status!="ok":
                return False, "duplicate"

        old = node.value

        if value == 0:
            node.history.append((old, value, "clear"))
            node.value = 0
            self.undo.push(row, col, old, value)
            self.grid.print_board()
            return True, "ok"

        valid = self.is_valid_move(row, col, value)
        solvable = self.is_solvable_after_move(row, col, value)

        if not valid or not solvable:
            node.history.append((old, value, "invalid"))
            node.value = value
            self.undo.push(row, col, old, value)
            self.grid.print_board()
            return True, "invalid"

        node.history.append((old, value, "ok"))
        node.value = value
        self.undo.push(row, col, old, value)
        self.grid.print_board()
        return True, "ok"

    def undo_last(self): # Undo the last move
        action = self.undo.pop()
        if action is None:
            return False
        r, c, old_value, new_value = action
        node = self.grid.get_node(r, c)
        node.value = old_value
        self.grid.print_board()
        return True

    def load_puzzle(self, puzzle): # Load a puzzle from a 2D list
        cur = self.grid.head
        for r in range(9):
            for c in range(9):
                v = puzzle[r][c]
                cur.value = v
                cur.fixed = (v != 0)
                cur.history = []
                cur = cur.next

    
    def is_complete(self):
        board = self.board_values()
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return False
        return True
        
    def is_valid_board(self):
        board = self.board_values()

        for r in range(9):
            row = board[r]
            if len(set(row)) != 9:
                return False

        for c in range(9):
            col = []
            for r in range(9):
                col.append(board[r][c])
            if len(set(col)) != 9:
                return False

        for sr in range(0, 9, 3):
            for sc in range(0, 9, 3):
                block = []
                for r in range(sr, sr + 3):
                    for c in range(sc, sc + 3):
                        block.append(board[r][c])
                if len(set(block)) != 9:
                    return False

        return True

    def is_winner(self):
        if not self.is_complete():
            return False
        if not self.is_valid_board():
            return False
        return True


