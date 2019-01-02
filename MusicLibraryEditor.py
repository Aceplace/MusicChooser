import os
import tkinter as tk
from tkinter import filedialog, messagebox
import MusicLibrary as mL


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.library = None
        self.current_library_filename = None

        # Menu
        menu_bar = tk.Menu(self, tearoff=False)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label='Load Library', command=self.load_library)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.quit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menu_bar)

        self.library_frame = tk.Frame(self)
        self.library_frame.pack(side=tk.LEFT)
        self.category_om = tk.OptionMenu(self, tk.StringVar(), 'NONE')
        self.category_om.pack()

    def load_library(self):
        try:
            library_filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Music Library",
                                                          filetypes=(("json", "*.json"),))
            if library_filename:
                self.library = mL.load_library(library_filename)
                self.current_library_filename = library_filename
                self.refresh()
        except Exception as e:
            messagebox.showerror('Open Library Error', e)

    def refresh(self):
        self.category_om['menu'].delete(0, 'end')
        for category in self.library['categories'].keys():
            self.category_om['menu'].add_command(label=category, command=lambda c=category: self.choose_category(c))

    def choose_category(self, value):
        print(value)


if __name__ == '__main__':
    root = App()
    root.mainloop()
