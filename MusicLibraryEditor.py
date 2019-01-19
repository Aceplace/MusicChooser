import os
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox
import MusicLibrary as ml
import sys


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.library = None
        self.current_library_filename = None
        self.current_category = None
        self.weight_validate_command = (self.register(self.weight_validate), '%P', '%W')
        self.loading_weights = False

        # Menu
        menu_bar = tk.Menu(self, tearoff=False)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label='Load Library', command=self.load_library)
        file_menu.add_command(label='Save Library', command=self.save_library)
        file_menu.add_command(label='Save Library As', command=self.save_library_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.quit)

        library_menu = tk.Menu(menu_bar, tearoff=False)
        library_menu.add_command(label='Create Library from Directory', command=self.create_library_from_directory)
        library_menu.add_command(label='Update Library', command=self.update_library)
        library_menu.add_command(label='Write Out Library Songlist', command=self.write_song_list_to_file)
        library_menu.add_command(label='Reset repeat data', command=self.reset_repeat_data)

        menu_bar.add_cascade(label='File', menu=file_menu)
        menu_bar.add_cascade(label='Library', menu=library_menu)
        self.config(menu=menu_bar)

        # Library Frame
        self.grid_columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        library_frame = tk.Frame(self)
        library_frame.grid(row=0, column=0, sticky='NWS')
        library_frame.rowconfigure(3, weight=1)

        # Library Frame -> Category Chooser
        tk.Label(library_frame, text='Categories').grid(row=0, column=0)
        self.category_om = tk.OptionMenu(library_frame, tk.StringVar(), 'NONE')
        self.category_om.grid(row=1, column=0)

        # Library Frame -> Song Name Listbox
        tk.Label(library_frame, text='Song Names').grid(row=2, column=0)

        song_name_lb_frame = tk.Frame(library_frame)
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
        priorities_frame = tk.Frame(library_frame)
        priorities_frame.grid(row=3, column=1, sticky='NW')
        tk.Label(priorities_frame, text='Set Priorities:').pack()
        for i in range(10):
            tk.Button(priorities_frame, text=f' {i} ', command=lambda p=i: self.set_priority(p)).pack()

        # Priority Weights Frame
        priority_weights_frame = tk.Frame(self)
        priority_weights_frame.grid(row=0, column=1, sticky='NW')

        tk.Label(priority_weights_frame, text='Priority Weights').grid(row=0, column=0)
        self.weight_modifier_widgets = []
        for i in range(10):
            entry_var = tk.StringVar()  # Used to detect changes to weight entries and automatically update stuff
            entry_var.trace_add('write', self.weight_entry_callback)
            weight_entry = tk.Entry(priority_weights_frame, textvariable=entry_var, validate="key",
                                    validatecommand=self.weight_validate_command)
            entry_var.set('0')
            weight_label = tk.Label(priority_weights_frame, text=f'Priority: {i}\tWaiting for Loaded Library')
            weight_entry.grid(row=i+1, column=0)
            weight_label.grid(row=i+1, column=1, sticky='W')
            self.weight_modifier_widgets.append((weight_entry, weight_label, entry_var))

    def weight_entry_callback(self, *args):
        if self.loading_weights:
            return
        if self.library:
            self.library['weights'] = [int(weight_widgets[0].get()) for weight_widgets in self.weight_modifier_widgets]
            self.refresh_weight_labels()


    def refresh_weight_labels(self):
        relative_frequencies = ml.calculate_relative_frequency(self.library, 40)
        for priority, weight_label in enumerate(list(zip(*self.weight_modifier_widgets))[1]):
            if relative_frequencies[priority] == '--':
                weight_label_text = f'Priority: {priority}'
            else:
                weight_label_format = 'Priority: {}, {} Songs in priority. Each song will' +\
                                    ' appear in 1 out of every {:.2f} playlists'
                weight_label_text = weight_label_format.format(priority,
                                                        ml.get_number_of_songs_for_priority(self.library, priority),
                                                        float(relative_frequencies[priority]))
            weight_label.configure(text=weight_label_text)


    def load_library(self, library_filename=None):
        try:
            if not library_filename:
                library_filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Music Library",
                                                              filetypes=(("json", "*.json"),))

            if library_filename:
                self.library = ml.load_library(library_filename)
                self.current_library_filename = library_filename
                self.current_category = None
                self.refresh_category_om()
                self.refresh_song_lb(None)
                self.load_weights()
        except Exception as e:
            print(traceback.print_exc())
            messagebox.showerror('Open Library Error', e)

    def create_library_from_directory(self):
        try:
            library_directory = filedialog.askdirectory()

            if library_directory:
                self.library = ml.create_library(library_directory)
                self.current_library_filename = None
                self.current_category = None
                self.refresh_category_om()
                self.refresh_song_lb(None)
                self.load_weights()
        except Exception as e:
            print(traceback.print_exc())
            messagebox.showerror('Create Library Error', e)

    def update_library(self):
        if not self.library:
            return

        try:
            library_directory = filedialog.askdirectory()

            if library_directory:
                self.library = ml.get_updated_library(self.library, library_directory)
                self.current_category = None
                self.refresh_category_om()
                self.refresh_song_lb(None)
                self.load_weights()
        except Exception as e:
            print(traceback.print_exc())
            messagebox.showerror('Create Library Error', e)


    def save_library(self):
        try:
            if self.current_library_filename:
                ml.save_library(self.library, self.current_library_filename)
            else:
                self.save_library_as()
        except Exception as e:
            print(traceback.print_exc())
            messagebox.showerror('Create Library Error', e)

    def save_library_as(self):
        try:
            library_filename = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                                            title='Save music library',
                                                            filetypes=(('json', '*.json'),),
                                                            defaultextension='.json')
            if library_filename:
                ml.save_library(self.library, library_filename)
                self.current_library_filename = library_filename
        except Exception as e:
            print(traceback.print_exc())
            messagebox.showerror('Create Library Error', e)

    def write_song_list_to_file(self):
        if not self.library:
            return

        try:
            song_list_file_name = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                                            title='Library Song List',
                                                            filetypes=(('Text File', '*.txt'),),
                                                            defaultextension='.txt')
            if song_list_file_name:
                ml.write_song_list(self.library, song_list_file_name)
        except Exception as e:
            print(traceback.print_exc())
            messagebox.showerror('Write song list error.', e)

    def reset_repeat_data(self):
        if self.library:
            ml.reset_repeat_data(self.library)

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


    def load_weights(self):
        self.loading_weights = True # This prevents weight entry callback from modifying library while library is writing into it
        for priority in range(10):
            self.weight_modifier_widgets[priority][2].set(str(self.library['weights'][priority]))
        self.loading_weights = False
        self.refresh_weight_labels()


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
        self.refresh_weight_labels()

    def weight_validate(self, new_value, widget_name):
        # pre validation
        entry_widget = self.nametowidget(widget_name)
        entry_widget.config(validate=None, validatecommand=None)
        if len(new_value) == 0:
            for priority, entry_widget_check in enumerate(list(zip(*self.weight_modifier_widgets))[0]):
                if entry_widget is entry_widget_check:
                    self.weight_modifier_widgets[priority][2].set('0')
        elif len(new_value) == 2 and new_value[0]=='0' and new_value[1].isdigit():
            for priority, entry_widget_check in enumerate(list(zip(*self.weight_modifier_widgets))[0]):
                if entry_widget is entry_widget_check:
                    self.weight_modifier_widgets[priority][2].set(new_value[1])
        entry_widget.config(validate='key', validatecommand=self.weight_validate_command)

        if len(new_value) > 1 and new_value[0]=='0':
            return False
        try:
            int_value = int(new_value)
            if int_value >= 0:
                return True
            return False
        except ValueError:
            return False


if __name__ == '__main__':
    root = App()
    try:
        library_file_path = sys.argv[1]
        root.load_library(library_file_path)
    except Exception:
        pass
    root.mainloop()
