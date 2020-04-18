import datetime
import os
import socket
import tkinter as tk
from tkinter import ACTIVE, END, ttk

CLIENT_PORT = 8888


class Application(tk.Frame):
    '''

    '''

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

        self.FILE_TRACKER_IP = '127.0.1.1'
        self.FILE_TRACKER_PORT = '9999'

    def is_valid_ip_port(self, ip_line, port_line):
        return True

    def get_files_info(self):
        target_directory = os.getcwd() + '/files'
        entries = os.listdir(target_directory)
        result = []

        for entry in entries:
            entry_full_dir = target_directory + '/' + entry
            entry_size = os.path.getsize(entry_full_dir)
            entry_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(entry_full_dir))
            entry_modified = entry_modified.strftime("%d/%m/%y")
            entry_name, entry_type = entry.split('.')
            result.append([entry_name, entry_type, entry_size, entry_modified])

        return result

    def get_connection_message_for_ft(self, files):
        message = ""

        for file_info in files:
            for file_data in file_info:
                message = f"{message}{file_data},"
            message = message + '\n'

        return message

    def connect_to_ft(self):
        entry_line = self.ft_server_entry.get()
        ip_line, port_line = entry_line.split(':')

        if self.is_valid_ip_port(ip_line, port_line):
            self.FILE_TRACKER_IP = ip_line
            self.FILE_TRACKER_PORT = port_line

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', CLIENT_PORT))

            try:
                self.socket.connect((self.FILE_TRACKER_IP, int(self.FILE_TRACKER_PORT)))
                self.socket.send("HELLO".encode())

                data = self.socket.recv(1024).decode("utf-8")
                print(f"Recieved: {data} from: {self.FILE_TRACKER_IP}:{self.FILE_TRACKER_PORT}")

                if data == "HI":
                    files = self.get_files_info()
                    message_to_ft = self.get_connection_message_for_ft(files)
                    self.socket.send(message_to_ft.encode())
                    self.ft_connection_message['text'] = "Connected to FT Server"
                    self.ft_connection_message['fg'] = "green"
                    self.ft_server_connection_button['state'] = "disabled"
                    self.ft_server_disconnect_button['state'] = "normal"
                else:
                    print("Not a HI message")
                
                self.socket.close()

            except:
                self.socket.close()
                print("Socket is closed")

        else:
            # TODO(ginet) show error message usig self.ft_connection_message
            pass

    def disconnect_from_ft(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Recreated socket")
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', CLIENT_PORT))
        print("Binded to the port")

        try:
            print(f"Connecting to {self.FILE_TRACKER_IP} at port {self.FILE_TRACKER_PORT}..")
            self.socket.connect((self.FILE_TRACKER_IP, int(self.FILE_TRACKER_PORT)))
            print("Connected to server")
            self.socket.send("BYE".encode())
            print("Send a message")
            self.socket.close()

            self.ft_connection_message['text'] = 'Disconnected from FT Server'
            self.ft_connection_message['fg'] = 'black'
            self.ft_server_connection_button['state'] = 'normal'
            self.ft_server_disconnect_button['state'] = 'disable'

        except KeyboardInterrupt:
            self.socket.close()
            print("Socket is closed")
        

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
            self.ft_back_frame, text="Disconnect", command=self.disconnect_from_ft, state='disabled')
        self.ft_server_disconnect_button.grid(row=1, column=1)

        self.ft_connection_message = tk.Label(
            self.ft_back_frame, text="No connection")
        self.ft_connection_message.grid(row=2, column=0, columnspan=2)

        self.first_separator = ttk.Separator(
            self.ft_back_frame, orient="horizontal")
        self.first_separator.grid(row=3, column=0, columnspan=2, sticky="ew")

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
