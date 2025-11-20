# Node untuk Linked List
class Node:
    def __init__(self, row, col, value=0, fixed=False):
        self.row = row
        self.col = col
        self.value = value
        self.fixed = fixed
        self.history = []
        self.next = None

#Linked List untuk grid 9x9
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
        self.index[(row, col)].value = value


#Stack untuk Undo
class UndoStack:
    def __init__(self):
        self.stack = []

    def push(self, row, col, old_value):
        self.stack.append((row, col, old_value))

    def pop(self):
        return self.stack.pop() if self.stack else None


#Sudoku Board
class SudokuBoard:
    def __init__(self):
        self.grid = LinkedList()
        self.undo_stack = UndoStack()

    #PRINT BOARD
    def print_board(self):
        print("-------------------------")
        for r in range(9):
            row_str = ""
            for c in range(9):
                val = self.grid.get(r, c).value
                if c % 3 == 0:
                    row_str += "| "
                row_str += (str(val) if val != 0 else ".") + " "
            row_str += "|"
            print(row_str)
            if r % 3 == 2:
                print("-------------------------")

    #VALIDASI
    def is_valid_horizontal(self, row, col, value):
        for c in range(9):
            if c != col and self.grid.get(row, c).value == value:
                return False
        return True

    def is_valid_vertical(self, row, col, value):
        for r in range(9):
            if r != row and self.grid.get(r, col).value == value:
                return False
        return True

    def is_valid_subgrid(self, row, col, value):
        start_r = (row // 3) * 3
        start_c = (col // 3) * 3

        for r in range(start_r, start_r + 3):
            for c in range(start_c, start_c + 3):
                if not (r == row and c == col) and self.grid.get(r, c).value == value:
                    return False
        return True

    #CEK
    def can_place(self, row, col, value):
        return (self.is_valid_horizontal(row, col, value) and
                self.is_valid_vertical(row, col, value) and
                self.is_valid_subgrid(row, col, value))

    #SET + UNDO
    def set_value(self, row, col, value):
        node = self.grid.get(row, col)
        if node.fixed:
            print("Cannot change a fixed cell.")
            return False
        old_value = node.value
        self.undo_stack.push(row, col, old_value)
        node.history.append(old_value)
        if value != 0 and not self.can_place(row, col, value):
            print("Invalid move!")
            return False
        
        node.value = value
        return True

    def undo(self):
        last = self.undo_stack.pop()
        if last:
            row, col, old_value = last
            self.grid.set(row, col, old_value)
        else:
            print("Nothing to undo.")

    #FIND EMPTY
    def find_empty(self):
        for r in range(9):
            for c in range(9):
                if self.grid.get(r, c).value == 0:
                    return r, c
        return None

    #SOLVER
    def solve(self):
        empty = self.find_empty()
        if not empty:
            return True

        row, col = empty

        for num in range(1, 10):
            if self.can_place(row, col, num):
                self.grid.set(row, col, num)

                if self.solve():
                    return True

                self.grid.set(row, col, 0)

        return False

    def is_board_valid(self):
        # cek baris
        for r in range(9):
            seen = set()
            for c in range(9):
                val = self.grid.get(r, c).value
                if val != 0:
                    if val in seen:
                        return False
                    seen.add(val)

        # cek kolom
        for c in range(9):
            seen = set()
            for r in range(9):
                val = self.grid.get(r, c).value
                if val != 0:
                    if val in seen:
                        return False
                    seen.add(val)

        # cek subgrid
        for sr in range(0, 9, 3):
            for sc in range(0, 9, 3):
                seen = set()
                for r in range(sr, sr+3):
                    for c in range(sc, sc+3):
                        val = self.grid.get(r, c).value
                        if val != 0:
                            if val in seen:
                                return False
                            seen.add(val)

        return True

    def reset(self):
        for r in range(9):
            for c in range(9):
                self.grid.set(r, c, 0)
        self.undo_stack = UndoStack()
