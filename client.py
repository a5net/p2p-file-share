import tkinter as tk
from tkinter import END, ACTIVE
from tkinter import ttk

FILE_TRACKER_IP = '192.168.0.0'
FILE_TRACKER_PORT = '9999'

CLIENT_PORT = '8888'


class Application(tk.Frame):
    '''

    '''

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def connect_to_ft(self):
        pass

    def disconnect_from_ft(self):
        pass

    def build_ft_server_widgets(self):
        self.ft_back_frame = tk.Frame(self.master, width=500, height=300)
        self.ft_back_frame.grid()

        self.ft_server_connection_text = tk.Label(
            self.ft_back_frame, text="IP Address(ex: 10.10.10.1:3000)")
        self.ft_server_connection_text.grid(row=0, column=0)

        self.ft_server_entry = tk.Entry(self.ft_back_frame)
        self.ft_server_entry.grid(row=0, column=1)

        self.ft_server_connection_button = tk.Button(
            self.ft_back_frame, text="Connect", command=self.connect_to_ft)
        self.ft_server_connection_button.grid(row=1, column=0)

        self.ft_server_disconnect_button = tk.Button(
            self.ft_back_frame, text="Disconnect", command=self.disconnect_from_ft)
        self.ft_server_disconnect_button.grid(row=1, column=1)

        self.first_separator = ttk.Separator(
            self.ft_back_frame, orient="horizontal")
        self.first_separator.grid(row=2, column=0, columnspan=2, sticky="ew")

    def build_search_widgets(self):
        self.back_frame = tk.Frame(self.master, width=500, height=500)
        self.back_frame.grid()

        self.file_name_label = tk.Label(self.back_frame, text="File Name")
        self.file_name_label.grid(row=0, column=0)

        self.search_bar_entry = tk.Entry(self.back_frame)
        self.search_bar_entry.grid(row=0, column=1)

        self.search_bar_button = tk.Button(
            self.back_frame, text="Search", command=self.search_button_action)
        self.search_bar_button.grid(row=0, column=3)

        self.search_list = tk.Listbox(self.back_frame, width=40, height=20)
        self.search_list.grid(row=1, column=0, columnspan=4)

        self.download_button = tk.Button(
            self.back_frame,  text="Download File")
        self.download_button.grid(row=2, column=1)

    def create_widgets(self):
        self.build_ft_server_widgets()
        self.build_search_widgets()

    def search_button_action(self):
        entry_value = self.search_bar_entry.get()
        file_list = self.ft_server_dowload_request(entry_value)
        row = 0

        self.search_list.delete(0, END)

        for file in file_list:
            self.search_list.insert(row, file)
            row = row + 1

    def ft_server_dowload_request(self, file_name):
        return [file_name + '.tmp', file_name + '.mp4', file_name+'.txt']


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
