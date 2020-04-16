import tkinter as tk

class Application(tk.Frame):
    '''
        back: tk.Frame()
        hi_there: tk.Button()
        quit: tk.Button()
    '''
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
       # self.create_main_window()
        self.create_widgets()

    def create_widgets(self):
        self.back_frame = tk.Frame(self.master, width=500, height=500)
        self.back_frame.grid()

        self.file_name_label = tk.Label(self.back_frame, text="File Name")
        self.file_name_label.grid(row=0, column=0)

        self.search_bar_entry = tk.Entry(self.back_frame)
        self.search_bar_entry.grid(row=0, column=1)

        self.search_bar_button = tk.Button(self.back_frame, text="Search")
        self.search_bar_button.grid(row=0, column=3)

        self.search_list = tk.Listbox(self.back_frame, width=40, height=20)
        self.search_list.grid(row=1, column=0, columnspan=4)
        self.search_list.insert(0, "movie.mp4")

        self.download_button = tk.Button(self.back_frame,  text = "Download File")
        self.download_button.grid(row=2, column=1)

        

    def say_hi(self):
        print("hi there, everyone!")


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()    
