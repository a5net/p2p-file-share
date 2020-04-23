import socket
import os

from _thread import start_new_thread
import threading

HELLO_MESSAGE = "HELLO"
HELLO_MESSAGE_RESPONSE = "HI"

db = dict()  # Create empty dictionary (tuple -> list[int])


def deserialize_files(files):
    files = files.split('\n')
    result = []
    for file_config in files:
        result.append(file_config.split(','))
    return result[:-1]


def append_ip_and_port(files, addr):
    for file in files:
        file[-1] = addr[0]
        file.append(str(addr[1]))


def process_hello_message(conn, addr):
    conn.send(HELLO_MESSAGE_RESPONSE.encode())
    files = conn.recv(1024).decode("utf-8")

    files_to_store = deserialize_files(files)

    if (len(files_to_store) > 0):
        append_ip_and_port(files_to_store, addr)
        print(f"{len(files_to_store)} file(-s) from {addr} has been stored")
        db[addr] = files_to_store
    else:
        print(f"No data from {addr}, not allowing to enter FT Server")

    conn.close()


def process_bye_message(conn, addr):
    result = db.pop(addr, None)
    if result:
        print(f"Entry {addr} removed from storage")
    else:
        print(f"Entry {addr} is not found in storage")
    conn.close()


def process_search_message(conn, addr, data):
    file_name = data[7:] # removes first part of the message ("SEARCH:")

    if not addr in db:
        conn.close()
        print(f"No data from {addr}, not allowing search FT Server data")
        return

    files_to_send = []
    for key in db.keys():
        entry = db[key]
        for file_data in entry:
            print(f"File Data: {file_data}")
            if file_name in file_data:
                files_to_send.append(file_data)

    if len(files_to_send) == 0:
        conn.send("NOT FOUND".encode())
    else:
        message = "FOUND:"
        for file_info in files_to_send:
            print(file_info)
            file_data = ",".join(file_info)
            message = f"{message}{file_data}\n"
        conn.send(message.encode())
    conn.close()


def process_connection(conn, addr):
    while conn:
        data = conn.recv(1024)

        if not data or len(data) == 0:
            print("No data")
            break

        data = data.decode("utf-8")
        print(f"Recieved data: {data} from: {addr}")

        if data.startswith("HELLO"):
            process_hello_message(conn, addr)
        elif data.startswith("BYE"):
            process_bye_message(conn, addr)
        elif data.startswith("SEARCH"):
            process_search_message(conn, addr, data)
        
        break


def main():
    print("Launching File Tracker(FT) Server")
    port_number = input("Please enter the port number: ")

    while not port_number.isnumeric():
        port_number = input("Please enter a number e.g. 9999")

    port_number = int(port_number)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port_number))

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print("=============================")
    print(f"IP Address: {ip_address}")
    print(f"Port: {port_number}")
    print("Please use the information above to connect to FT Server")
    print("=============================")

    try:
        while True:
            print("Waiting for connection...")
            s.listen()
            conn, addr = s.accept()
            start_new_thread(process_connection, (conn, addr,))
        s.close()
    except KeyboardInterrupt:
        s.close()
        print("Socket is closed")


if __name__ == "__main__":
    main()
