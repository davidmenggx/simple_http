import socket
import threading
import signal

from utilities import get_headers, get_request_line

HOST = '127.0.0.1'
PORT = 1738

RUNNING = True

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def signal_shutdown(_sig, _frame) -> None:
    global RUNNING
    RUNNING = False

signal.signal(signal.SIGINT, signal_shutdown) # Catch CTRL+C
signal.signal(signal.SIGTERM, signal_shutdown) # Catch kill command

def handle_connection(connection: socket.socket) -> None:
    with connection as s:
        buffer = bytearray()
        header_delimiter = b'\r\n\r\n'

        while header_delimiter not in buffer:
            chunk = connection.recv(1024)
            if not chunk:
                break
            buffer.extend(chunk)
        
        headers_raw, _, remaining = buffer.partition(header_delimiter)
        headers = headers_raw.decode('utf-8')

        content_length = 0 # important, read this from the header

        body = bytearray(remaining)

        while len(body) < content_length:
            bytes_to_read = content_length - len(body)
            chunk = s.recv(min(bytes_to_read, 4096))
            if not chunk:
                break
            body.extend(chunk)


        # load the data into the buffer, up until the double crlf
        # then parse the buffer (after decoding to utf) and extract the request line and then headers
        # then, after capturing the message length from headers, read the body directly
        # then process the request based on the method

def main() -> None:
    with sock as s:
        s.bind((HOST, PORT))
        s.listen()
        s.settimeout(1.0)
        while RUNNING:
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue

            connection_worker = threading.Thread(target=handle_connection, args=(conn,), daemon=True)
            connection_worker.start()

if __name__ == '__main__':
    main()