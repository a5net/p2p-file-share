import socket
import os

HELLO_MESSAGE = "HELLO"
HELLO_MESSAGE_RESPONSE = "HI"

db = dict() # Create empty dictionary (tuple -> list[int])


def deserialize_files(files):
    files = files.split('\n')
    result = []
    for file_config in files:
        result.append(file_config.split(','))
    return result[:-1]


def process_connection(conn, addr):
    while conn:
        data = conn.recv(1024)
        if not data or len(data) == 0:
            print("No data")
            break

        data = data.decode("utf-8")
        print(f"Recieved data: {data} from: {addr}")

        if data == "HELLO":
            conn.send(HELLO_MESSAGE_RESPONSE.encode())
            files = conn.recv(1024).decode("utf-8")
            
            files_to_store = deserialize_files(files)

            if (len(files_to_store) > 0):
                print(f"{len(files_to_store)} file(-s) from {addr} has been stored")
                db[addr] = files_to_store
            else:
                print(f"No data from {addr}, not allowing to enter FT Server")

            conn.close()
            break
            

        else:
            #TODO(ginet) respond to other messages
            print("Not a HELLO message")
            conn.close()
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
            with conn:
                process_connection(conn, addr)

        s.close()

    except KeyboardInterrupt:
        s.close()
        print("Socket is closed")
    



if __name__ == "__main__":
    main()
