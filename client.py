import datetime
import os
import socket
import tkinter as tk
from tkinter import ACTIVE, END, ttk
import threading
import re


ip_regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''


class ListeningThread(threading.Thread):
    def __init__(self, socket, port_number, control_flag):
        threading.Thread.__init__(self)
        self.socket = socket
        self.port_number = port_number
        self.control_flag = control_flag

    def process_request(self, conn, addr):
        while conn and self.control_flag:
            data = conn.recv(1024)
            if not data or len(data) == 0:
                print("No data")
                break

            if b"DOWNLOAD" in data:
                command, file_info  = data.decode("utf-8").split(':')
                file_name, file_type, file_size = file_info.split(',')

                target_directory = os.getcwd() + '/files'
                available_files = os.listdir(target_directory)

                if f"{file_name}.{file_type}" in available_files:
                    full_directory = target_directory + '/' + file_name + '.' + file_type
                    f = open(full_directory, 'rb')
                    buffer = f.read(1024)
                    conn.send("FILE: ".encode())
                    print(f"Sending file located at: {full_directory}")
                    while buffer:
                        print(f"Sending {file_name + '.' + file_type} to {addr}")
                        conn.send(buffer)
                        buffer = f.read(1024)
                    print(
                        f"File was sent successfully, closing connection with {addr}")
                    f.close()
                    conn.close()
                    break
            

    def run(self):
        print("Thread created")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.get_host_ip(), self.port_number))

        try:
            while self.control_flag:
                self.socket.listen()
                conn, addr = self.socket.accept()
                with conn:
                    self.process_request(conn, addr)

            self.socket.close()
        except KeyboardInterrupt:
            self.stop()
            self.socket.close()

        print("Thread is terminated")

    def get_host_ip(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address


    def is_my_ip_port(self, ip, port):
        return ip == self.get_host_ip and port == self.port_number 


    def stop(self):
        self.control_flag = False
        self.killer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.killer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.killer_socket.bind(('', self.port_number + 666))
        self.killer_socket.connect((self.get_host_ip(), self.port_number))
        self.killer_socket.close()



class Application(tk.Frame):

    def __init__(self, master=None):
        # GUI Interface builder
        super().__init__(master)
        self.master = master
        self.create_widgets()

        # Default values for TCP Connection
        self.FILE_TRACKER_IP = '127.0.1.1'
        self.FILE_TRACKER_PORT = '9999'
        self.CLIENT_IP = self.get_host_ip()
        self.CLIENT_PORT = 8888

        # Thread defaults for listening thread
        self.control_flag = True


    def is_valid_ip_port(self, ip_line, port_line):
        return re.search(ip_regex, ip_line) and port_line.isnumeric()


    def get_host_ip(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address


    def is_my_ip_port(self, ip, port):
        print(f"host ip: {ip} my ip: {self.get_host_ip()} equal: {ip == self.get_host_ip()}")
        print(
            f"host port: {port} my port: {self.CLIENT_PORT} equal: {port == self.CLIENT_PORT}")

        return (ip == self.get_host_ip()) and (port == self.CLIENT_PORT)


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

    def write_to_connection_message(self, message, color='black'):
        self.ft_connection_message['text'] = message
        self.ft_connection_message['fg'] = color


    def connect_to_ft(self):
        entry_line = self.ft_server_entry.get()

        try:
            ip_line, port_line = entry_line.split(':')
        except ValueError:
            self.write_to_connection_message("Wrong format for FT Server Address", "red")
            return

        if self.is_valid_ip_port(ip_line, port_line):
            self.FILE_TRACKER_IP = ip_line
            self.FILE_TRACKER_PORT = port_line
            
            try:
                self.CLIENT_PORT = int(self.ft_server_my_port_entry.get())
            except ValueError:
                self.write_to_connection_message("Wrong format for Port Number", "red")
                return

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                self.socket.bind((self.CLIENT_IP, self.CLIENT_PORT))
            except OSError:
                self.write_to_connection_message("Socket number already in use, please choose other", "dark orange")
                self.socket.close()
                return


            try:
                self.socket.connect((self.FILE_TRACKER_IP, int(self.FILE_TRACKER_PORT)))
                self.socket.send("HELLO".encode())

                data = self.socket.recv(1024).decode("utf-8")
                self.write_to_server_message(f"Recieved: {data} from: {self.FILE_TRACKER_IP}:{self.FILE_TRACKER_PORT}")

                if data == "HI":
                    files = self.get_files_info()
                    message_to_ft = self.get_connection_message_for_ft(files)
                    self.socket.send(message_to_ft.encode())
                    self.ft_connection_message['text'] = "Connected to FT Server"
                    self.ft_connection_message['fg'] = "green"
                    self.ft_server_connection_button['state'] = "disabled"
                    self.ft_server_disconnect_button['state'] = "normal"
                else:
                    self.write_to_connection_message("No files are recieved by FT Server, please add some to files folder", "black")
                
                self.socket.close()
                self.listening_thread = ListeningThread(self.socket, self.CLIENT_PORT, self.control_flag)
                self.listening_thread.start()


            except:
                self.socket.close()
                print("Socket is closed")

        else:
            # TODO(ginet) show error message usig self.ft_connection_message
            self.write_to_connection_message(
                "Wrong format for FT Server Address", "red")
            pass


    def disconnect_from_ft(self):
        self.listening_thread.stop()
        self.listening_thread.join()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.CLIENT_IP, self.CLIENT_PORT))

        try:
            self.socket.connect((self.FILE_TRACKER_IP, int(self.FILE_TRACKER_PORT)))
            self.socket.send("BYE".encode())
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
        self.ft_back_frame.grid(row=0, column=0)

        self.ft_server_connection_text = tk.Label(
            self.ft_back_frame, text="FT Server(ex: 10.10.10.1:3000)")
        self.ft_server_connection_text.grid(row=0, column=0)

        self.ft_server_entry = tk.Entry(self.ft_back_frame)
        self.ft_server_entry.grid(row=0, column=1)

        self.ft_server_my_port_text = tk.Label(self.ft_back_frame, text="My port number(ex: 8888)")
        self.ft_server_my_port_text.grid(row=1, column=0)

        self.ft_server_my_port_entry = tk.Entry(self.ft_back_frame)
        self.ft_server_my_port_entry.grid(row=1, column=1)

        self.ft_server_connection_button = tk.Button(
            self.ft_back_frame, text="Connect", command=self.connect_to_ft)
        self.ft_server_connection_button.grid(row=2, column=0)

        self.ft_server_disconnect_button = tk.Button(
            self.ft_back_frame, text="Disconnect", command=self.disconnect_from_ft, state='disabled')
        self.ft_server_disconnect_button.grid(row=2, column=1)

        self.ft_connection_message = tk.Label(
            self.ft_back_frame, text="No connection")
        self.ft_connection_message.grid(row=3, column=0, columnspan=2)


    def write_to_server_message(self, message):
        self.message_from_server.config(state=tk.NORMAL)
        self.message_from_server.delete('1.0', END)
        self.message_from_server.tag_configure("center", justify='center')
        self.message_from_server.insert(END, message)
        self.message_from_server.tag_add("center", "1.0", "end")
        self.message_from_server.config(state=tk.DISABLED)


    def build_search_bar_widgets(self):
        self.search_bar_frame = tk.Frame(self.master, width=500, height=500)
        self.search_bar_frame.grid(row=2, column=0)

        self.file_name_label = tk.Label(self.search_bar_frame, text="File Name")
        self.file_name_label.grid(row=0, column=0)

        self.search_bar_entry = tk.Entry(self.search_bar_frame)
        self.search_bar_entry.grid(row=0, column=1)

        self.search_bar_button = tk.Button(
            self.search_bar_frame, text="Search", command=self.search_button_action)
        self.search_bar_button.grid(row=0, column=2)

        self.vertical_separator = ttk.Separator(
            self.search_bar_frame, orient="vertical")
        self.vertical_separator.grid(
            row=0, column=3, sticky="ns")

        self.message_from_server = tk.Text(self.search_bar_frame, height=1, width=50, bg='light gray')
        self.write_to_server_message("No message to display")
        self.message_from_server.grid(row=0, column=4)


    def build_search_widgets(self):
        self.back_frame = tk.Frame(self.master, width=500, height=500)
        self.back_frame.grid(row=3, column=0)

        self.build_tree_view(self.back_frame)

        self.download_button = tk.Button(
            self.back_frame,  text="Download File", command=self.download_selected_file)
        self.download_button.grid(row=2, column=1)

    
    def build_tree_view(self, frame):
        self.tree = ttk.Treeview(frame)
        self.tree["columns"] = ("two", "three", "four", "five", "six")
        
        self.tree.column("#0", width=100, minwidth=100)
        self.tree.column("two", width=100, minwidth=100)
        self.tree.column("three", width=100, minwidth=100)
        self.tree.column("four", width=150, minwidth=150)
        self.tree.column("five", width=100, minwidth=100)
        self.tree.column("six", width=180, minwidth=180)

        self.tree.heading("#0", text="File Name", anchor=tk.W)
        self.tree.heading("two", text="File Type", anchor=tk.W)
        self.tree.heading("three", text="File Size", anchor=tk.W)
        self.tree.heading("four", text="Modified Date", anchor=tk.W)
        self.tree.heading("five", text="Owner IP", anchor=tk.W)
        self.tree.heading("six", text="Owner Port Number", anchor=tk.W)
        
        
        self.tree.grid(row=1, column=0, columnspan=3)


    def download_selected_file(self):
        self.download_button['state'] = 'disable'

        selected = self.tree.item(self.tree.focus())['values']

        if selected is None or len(selected) == 0:
            self.write_to_server_message("Nothing is selected")
            self.download_button['state'] = 'normal'
            return

        if self.ft_server_disconnect_button['state'] == 'disabled':
            self.write_to_server_message("Please connect to FT Server")
            self.download_button['state'] = 'normal'
            return

        ip_address = selected[3]
        port_number = int(selected[4])

        print(f"Connection to {ip_address} with type {type(ip_address)}")

        if self.is_my_ip_port(ip_address, port_number):
            self.write_to_server_message("Cannot connect to selected owner: owner is me")
            self.download_button['state'] = 'normal'
            return

        self.write_to_server_message(f"Trying to download from {ip_address}:{port_number}")

        file_name = self.tree.item(self.tree.focus())['text']
        file_type = selected[0]
        file_size = selected[1]

        self.listening_thread.stop()
        self.listening_thread.join()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.CLIENT_IP, self.CLIENT_PORT))

        try:
            self.socket.connect((ip_address, port_number))
            self.socket.send(
                f"DOWNLOAD:{file_name},{file_type},{file_size}".encode())

            output_file_name = file_name + '.' + file_type
            f = open("downloads/" + output_file_name, 'wb')
            buffer = self.socket.recv(1024)[6:]

            first_part = True
            while buffer or first_part:
                print(f"Recieving {file_name + '.' + file_type} from {ip_address + ':' + str(port_number)}")
                f.write(buffer)
                buffer = self.socket.recv(1024)
                first_part = False
            self.write_to_server_message("File Recieved! Saving the file")
            f.close()

        except:
            pass

        self.socket.close()
        
        self.control_flag = True
        self.listening_thread = ListeningThread(
            self.socket, self.CLIENT_PORT, self.control_flag)
        self.listening_thread.start()

        self.download_button['state'] = 'active'


    def create_widgets(self):
        self.build_ft_server_widgets()
        self.first_separator = ttk.Separator(
            self.master, orient="horizontal")
        self.first_separator.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.build_search_bar_widgets()
        self.build_search_widgets()


    def clear_search_results(self):
        self.tree.delete(*self.tree.get_children())

    def search_button_action(self):
        entry_value = self.search_bar_entry.get()

        if self.ft_server_disconnect_button['state'] == 'disabled':
            self.write_to_server_message("To search files, please connect to FT")
            return

        file_list = self.ft_server_dowload_request(entry_value)
        row = 0

        if (len(file_list) == 0):
            return

        self.write_to_server_message(f"Found {len(file_list)} file(-s)")
        self.clear_search_results()

        for file in file_list:
            self.tree.insert("", END, row, text=file[0], values=file[1:])
            row = row + 1

    def deserialize_files(self, files):
        files = files.split('\n')
        result = []
        for file_config in files:
            result.append(file_config.split(','))
        return result[:-1]


    def ft_server_dowload_request(self, file_name):
        self.clear_search_results()

        self.listening_thread.stop()
        self.listening_thread.join()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.CLIENT_IP, self.CLIENT_PORT))

        try:
            self.socket.connect(
                (self.FILE_TRACKER_IP, int(self.FILE_TRACKER_PORT)))
            self.socket.send(f"SEARCH:{file_name}".encode())

            data = self.socket.recv(1024).decode("utf-8")

            if not data:
                self.write_to_server_message(f"No reoponse. Please share files to make a search")
                pass

            print(
                f"Recieved: {data} from: {self.FILE_TRACKER_IP}:{self.FILE_TRACKER_PORT}")

            if data == "NOT FOUND":
                self.write_to_server_message(f"NOT FOUND message from {self.FILE_TRACKER_IP}:{self.FILE_TRACKER_PORT}")
                self.control_flag = True
                self.listening_thread = ListeningThread(
                    self.socket, self.CLIENT_PORT, self.control_flag)
                self.listening_thread.start()
                return []
            
            print("Raw data: " + data)
            files = self.deserialize_files(data[6:])

        except KeyboardInterrupt:
            self.socket.close()

        self.control_flag = True
        self.listening_thread = ListeningThread(
            self.socket, self.CLIENT_PORT, self.control_flag)
        self.listening_thread.start()
        return files


def main():
    root = tk.Tk()
    app = Application(master=root)
    root.resizable(0, 0)
    app.mainloop()


if __name__ == "__main__":
    main()
