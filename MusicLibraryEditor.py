import os
import tkinter as tk
from tkinter import filedialog, messagebox
import MusicLibrary as mL


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.library = None
        self.current_library_filename = None
        self.current_category = None

        # Menu
        menu_bar = tk.Menu(self, tearoff=False)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label='Load Library', command=self.load_library)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.quit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menu_bar)

        # Library Frame
        self.library_frame = tk.Frame(self)
        self.library_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.library_frame.rowconfigure(3, weight=1)

        # Library Frame -> Category Chooser
        tk.Label(self.library_frame, text='Categories').grid(row=0, column=0)
        self.category_om = tk.OptionMenu(self.library_frame, tk.StringVar(), 'NONE')
        self.category_om.grid(row=1, column=0)

        # Library Frame -> Song Name Listbox
        tk.Label(self.library_frame, text='Song Names').grid(row=2, column=0)

        song_name_lb_frame = tk.Frame(self.library_frame)
        song_name_lb_frame.grid(row=3, column=0, sticky='NS')
        song_name_lb_frame.grid_rowconfigure(0, weight=1)

        y_scroll = tk.Scrollbar(song_name_lb_frame, orient=tk.VERTICAL)
        y_scroll.grid(row=0, column=1, sticky='NS')
        x_scroll = tk.Scrollbar(song_name_lb_frame, orient=tk.HORIZONTAL)
        x_scroll.grid(row=1, column=0, sticky='WE')

        self.song_name_lb = tk.Listbox(song_name_lb_frame, xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set,
                                       selectmode=tk.EXTENDED)
        self.song_name_lb.grid(row=0, column=0, sticky='NS')
        x_scroll.config(command=self.song_name_lb.xview)
        y_scroll.config(command=self.song_name_lb.yview)

        # Library Frame -> Set Priorities
        priorities_frame = tk.Frame(self.library_frame)
        priorities_frame.grid(row=3, column=1, sticky='NW')
        tk.Label(priorities_frame, text='Set Priorities:').pack()
        for i in range(10):
            tk.Button(priorities_frame, text=f' {i} ', command=lambda p=i: self.set_priority(p)).pack()

    def load_library(self):
        try:
            library_filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Music Library",
                                                          filetypes=(("json", "*.json"),))
            if library_filename:
                self.library = mL.load_library(library_filename)
                self.current_library_filename = library_filename
                self.refresh_category_om()
                self.current_category = None
        except Exception as e:
            messagebox.showerror('Open Library Error', e)

    def refresh_category_om(self):
        self.category_om['menu'].delete(0, 'end')
        for category in self.library['categories'].keys():
            self.category_om['menu'].add_command(label=category, command=lambda c=category: self.refresh_song_lb(c))

    def refresh_song_lb(self, category):
        self.song_name_lb.delete(0, tk.END)
        self.current_category = category
        if not self.current_category:
            return
        for song in self.library['categories'][category]:
            insert_string = f"[ {song['priority']} ] {song['artist_name']} - {song['song_name']}"
            self.song_name_lb.insert(tk.END, insert_string)
        self.song_name_lb.config(width=0)

    def set_priority(self, priority):
        if not self.current_category:
            return

        selected_song_indexes = self.song_name_lb.curselection()
        y_view_fraction, _ = self.song_name_lb.yview()
        for lb_song_string in map(self.song_name_lb.get, selected_song_indexes):
            artist_name, song_name = map(str.strip, lb_song_string[5:].split('-'))
            song = [song for song in self.library['categories'][self.current_category]
                    if song['artist_name'] == artist_name and song['song_name'] == song_name][0]
            song['priority'] = priority

        self.refresh_song_lb(self.current_category)
        for i in selected_song_indexes:
            self.song_name_lb.selection_set(i)
        self.song_name_lb.yview_moveto(y_view_fraction)







if __name__ == '__main__':
    root = App()
    root.mainloop()
