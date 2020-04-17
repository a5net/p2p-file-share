import socket
import os


def process_connection(conn, addr):
    print("Connected by ", addr)
    while conn:
        data = conn.recv(1024)
        if not data or len(data) == 0:
            print("No data")
            break

        data = data.decode("utf-8")
        print("Recieved data: ", data)

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
    print("===========================")
    print(f"IP Address: {ip_address}")
    print(f"Port: {port_number}")
    print("\nPlease use the information above to connect to FT Server")
    print("===========================")

    try:
        while True:
            print("Waiting for connection...")
            s.listen()
            conn, addr = s.accept()
            with conn:
                process_connection(conn, addr)

        s.close()

    except:
        s.close()
        print("Socket is closed")
    



if __name__ == "__main__":
    main()
