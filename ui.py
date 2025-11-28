import tkinter as tk
from tkinter import messagebox
from coba import Sudoku

CELL_SIZE = 50
GRID_SIZE = 9
BLOCK_SIZE = 3

class SudokuUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sudoku Linked List")

        self.sudoku = Sudoku()
        self.selected = None

        self.canvas = tk.Canvas(
            master,
            width=CELL_SIZE * GRID_SIZE,
            height=CELL_SIZE * GRID_SIZE,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_click)
        self.master.bind("<Key>", self.on_key)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # contoh puzzle
        sample = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]

        self.sudoku.load_puzzle(sample)
        self.draw()

        tk.Button(master, text="Undo", command=self.undo).pack(pady=10)

    # ========================================================
    # Draw board
    # ========================================================
    def draw(self):
        self.canvas.delete("all")

        # highlight selection
        if self.selected:
            r, c = self.selected
            self.canvas.create_rectangle(
                c * CELL_SIZE, r * CELL_SIZE,
                (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE,
                fill="#CCE5FF", outline=""
            )

        # draw numbers
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                node = self.sudoku.grid.get(r, c)
                if node.value != 0:

                    # tentukan warna teks
                    if node.fixed:
                        color = "blue"
                    else:
                        # cek apakah history terakhir invalid
                        if node.history and node.history[-1][2] == "invalid":
                            color = "red"
                        else:
                            color = "black"

                    self.canvas.create_text(
                        c * CELL_SIZE + CELL_SIZE // 2,
                        r * CELL_SIZE + CELL_SIZE // 2,
                        text=str(node.value),
                        font=("Arial", 22),
                        fill=color
                    )

        # grid lines
        for i in range(GRID_SIZE + 1):
            lw = 3 if i % BLOCK_SIZE == 0 else 1
            self.canvas.create_line(0, i * CELL_SIZE,
                                    GRID_SIZE * CELL_SIZE, i * CELL_SIZE,
                                    width=lw)
            self.canvas.create_line(i * CELL_SIZE, 0,
                                    i * CELL_SIZE, GRID_SIZE * CELL_SIZE,
                                    width=lw)

    # ========================================================
    # Input Handling
    # ========================================================
    def on_click(self, event):
        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            self.selected = (r, c)
            self.draw()

    def on_key(self, event):
        if not self.selected:
            return

        if not event.char.isdigit():
            return

        val = int(event.char)
        r, c = self.selected

        success, status = self.sudoku.set_value(r, c, val)

        if status == "fixed":
            messagebox.showerror("Error", "Ini adalah angka fixed!")
        
        self.draw()

    # ========================================================
    # Undo
    # ========================================================
    def undo(self):
        self.sudoku.undo_last()
        self.draw()

    # ========================================================
    # Right-click History
    # ========================================================
    def on_right_click(self, event):
        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE
        if not (0 <= r < 9 and 0 <= c < 9):
            return

        node = self.sudoku.grid.get(r, c)

        win = tk.Toplevel(self.master)
        win.title(f"History ({r},{c})")
        win.geometry("280x350")

        tk.Label(win, text=f"Riwayat input cell ({r},{c})", font=("Arial", 12, "bold")).pack(pady=10)

        if not node.history:
            tk.Label(win, text="Tidak ada history", font=("Arial", 12)).pack()
            return

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True)

        for before, after, status in node.history:
            if status == "ok":
                text = f"{before} → {after}   (OK)"
            elif status == "invalid":
                text = f"{before} → {after}   (SALAH)"
            elif status == "clear":
                text = f"{before} → {after}   (HAPUS)"
            else:
                text = f"{before} → {after}"

            tk.Label(frame, text=text, font=("Arial", 12)).pack(anchor="w")


root = tk.Tk()
SudokuUI(root)
root.mainloop()
