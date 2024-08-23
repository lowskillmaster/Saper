import tkinter as tk
from random import shuffle
from collections import deque
from tkinter.messagebox import showinfo, showerror


class MyButton(tk.Button):
    def __init__(self, master, x: int, y: int, number: int, *args, **kwargs):
        super().__init__(master, width=3, font="Arial 15 bold", *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_of_mines = 0
        self.is_open = False

    def __str__(self):
        return f"[INFO]: coord({self.x};{self.y});num({self.number})"


class Minesweeper:
    colors = {
        1: "blue",
        2: "green",
        3: "red",
        4: "blue4",
        5: "brown",
        6: "cadetblue1",
        7: "black",
        8: "white   "
    }

    def __init__(self, row: int, column: int, mines: int):
        self.root = tk.Tk()
        self.root.title('Minesweeper')
        self.row = row
        self.column = column
        self.mines = mines
        self.count_of_flags = mines
        self.buttons = []

        self.flags_indexes = []

        self.game_over = False
        self.is_first_click = True
        self.create_field()

    def refresh(self):
        [child.destroy() for child in self.root.winfo_children()]

        self.buttons = []
        self.game_over = False
        self.is_first_click = True
        self.count_of_flags = self.mines
        self.create_field()

    def create_settings_win(self):
        window = tk.Toplevel(self.root)
        window.title('Settings')

        row_entry = tk.Entry(window)
        row_entry.insert(0, str(self.row))
        tk.Label(window, text="Number of lines: ").grid(row=0, column=0)
        row_entry.grid(row=0, column=1, padx=20, pady=20)

        column_entry = tk.Entry(window)
        column_entry.insert(0, str(self.column))
        tk.Label(window, text="Number of column: ").grid(row=1, column=0)
        column_entry.grid(row=1, column=1, padx=20, pady=20)

        mines_entry = tk.Entry(window)
        mines_entry.insert(0, str(self.mines))
        tk.Label(window, text="Number of Mines: ").grid(row=2, column=0)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)

        save_setting = tk.Button(window, text="Apply",
                                 command=lambda: self.change_settings(row_entry, column_entry, mines_entry))
        save_setting.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def change_settings(self, row: tk.Entry, column: tk.Entry, mines_entry: tk.Entry):
        try:
            int(row.get()), int(column.get()), int(mines_entry.get())
        except ValueError:
            showerror("Error", "Please enter a number")
            return
        self.row = int(row.get())
        self.column = int(column.get())
        self.mines = int(mines_entry.get())
        self.refresh()

    def create_field(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        settings_menu = tk.Menu(menu, tearoff=False)
        settings_menu.add_command(label='Play', command=self.refresh)
        settings_menu.add_command(label='Settings', command=self.create_settings_win)
        settings_menu.add_command(label='Quit', command=self.root.destroy)
        menu.add_cascade(label='Game', menu=settings_menu)

        count = 1
        for i in range(self.row):
            temp_buttons = []
            for j in range(self.column):
                current_button = MyButton(self.root, x=i, y=j, number=count)
                current_button.config(command=lambda button=current_button: self.click_button(button))
                current_button.bind("<Button-3>", self.click_right_button)
                current_button.grid(row=i, column=j, sticky=tk.EW)
                temp_buttons.append(current_button)
                count += 1
            self.buttons.append(temp_buttons)

        for i in range(self.row):
            self.root.rowconfigure(i, weight=1)

        for i in range(self.column):
            self.root.columnconfigure(i, weight=1)

        mines_label = tk.Label(self.root, text="Mines:", font="Arial 15 bold")
        mines_label.grid(row=self.row, column=0, columnspan=2)

        mines_count_label = tk.Label(self.root, font="Arial 15 bold")
        mines_count_label.grid(row=self.row, column=1, columnspan=2)
        mines_count_label['text'] = str(self.count_of_flags)

    def click_right_button(self, event):

        if self.game_over:
            showinfo('Game Over', f'You lose!\n'
                                  f'and find {self.mines - self.count_of_flags} mines')
            return

        mines_count_label = tk.Label(self.root, font="Arial 15 bold")
        mines_count_label.grid(row=self.row, column=1, columnspan=2)

        current_button = event.widget

        if current_button['state'] == 'normal':
            current_button['state'] = 'disabled'
            current_button['text'] = '⚑'

            self.count_of_flags -= 1
            mines_count_label['text'] = str(self.count_of_flags)

            self.flags_indexes.append(current_button.number)

            print(f"Номер флагов: {self.flags_indexes}, кол-во флажков: {self.count_of_flags}")

            current_button['disabledforeground'] = 'black'

        elif current_button['text'] == '⚑':
            self.count_of_flags += 1
            mines_count_label['text'] = str(self.count_of_flags)
            current_button['text'] = ''
            current_button['state'] = 'normal'
            self.flags_indexes.remove(current_button.number)

        self.check_won()

    def place_mines(self, number: int):

        indexes = list(range(1, self.row * self.column + 1))
        indexes.remove(number)
        shuffle(indexes)
        index_mines = indexes[:self.mines]
        for row_btn in self.buttons:
            for btn in row_btn:
                if btn.number in index_mines:
                    btn.is_mine = True

    def check_won(self):

        if self.count_of_flags == 0:
            mines_button = self.get_is_mine_buttons()
            set_flags_indexes = self.flags_indexes

            if sorted(mines_button) == sorted(set_flags_indexes):
                showinfo("UHU", f"YOU WON!\n"
                                f"and find all mines")
            else:
                showinfo("HOH", f"YOU LOSE!\n"
                                f"and find {self.count_of_flags_in_mines()}")
                self.open_all_buttons()
                self.game_over = True

    def get_is_mine_buttons(self):
        mine_buttons = []
        for btn_line in self.buttons:
            for btn in btn_line:
                if btn.is_mine:
                    mine_buttons.append(btn.number)
        return mine_buttons

    def count_mines(self):
        for i in range(self.row):
            for j in range(self.column):
                if not self.buttons[i][j].is_mine:
                    self.buttons[i][j].count_of_mines = self.get_mine_count(i, j)

    def log_game(self):
        print("___________________________")
        for i in range(self.row):
            for j in range(self.column):
                if self.buttons[i][j].is_mine:
                    print("B", end='')
                else:
                    print(self.buttons[i][j].count_of_mines, end='')
            print()

    def get_mine_count(self, x, y):
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if 0 <= x + dx < self.row and 0 <= y + dy < self.column:
                    if self.buttons[x + dx][y + dy].is_mine:
                        count += 1
        return count

    def click_button(self, button: MyButton):

        if button.is_open:
            return

        if self.is_first_click:
            self.place_mines(button.number)
            self.is_first_click = False
            self.count_mines()
            self.log_game()

        if button.is_mine:
            button.config(text='*', bg='red', disabledforeground='black')
            button.is_open = True
            self.open_all_buttons()
            self.game_over = True
            count_of_flags_in_mines = self.count_of_flags_in_mines()
            showinfo('Game Over', f'You lose!\n'
                                  f'and find {count_of_flags_in_mines} mines')
            self.open_all_buttons()
        else:
            if button.count_of_mines in Minesweeper.colors:
                color = Minesweeper.colors.get(button.count_of_mines, "orange")
                button.config(text=str(button.count_of_mines),
                              disabledforeground=color)
                button.is_open = True
            else:
                self.bfs(button)

        button.config(state="disabled")
        button.config(relief='sunken')

    def count_of_flags_in_mines(self):
        return sum([1 for i in self.flags_indexes if i in self.get_is_mine_buttons()])

    def bfs(self, button: MyButton):
        queue = deque([button])
        while queue:
            cur_btn = queue.popleft()
            color = Minesweeper.colors.get(cur_btn.count_of_mines, "orange")
            if cur_btn.count_of_mines:
                cur_btn.config(text=str(cur_btn.count_of_mines),
                               disabledforeground=color)
            else:
                cur_btn.config(text='', disabledforeground=color)

            cur_btn.is_open = True

            cur_btn.config(state="disabled")
            cur_btn.config(relief='sunken')

            if cur_btn.count_of_mines == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if 0 <= x + dx < self.row and 0 <= y + dy < self.column:
                            if not (dx == 0 and dy == 0):
                                next_btn = self.buttons[x + dx][y + dy]
                                if not next_btn.is_open and next_btn not in queue:
                                    queue.append(next_btn)

    def open_all_buttons(self):
        for i in range(self.row):
            for j in range(self.column):
                button = self.buttons[i][j]
                if button.is_mine:
                    button.config(text='*', disabledforeground='black')
                button.config(state="disabled")
                button.config(relief='sunken')


if __name__ == "__main__":
    game = Minesweeper(10, 10, 5)
    game.root.mainloop()
