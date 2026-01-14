import socket
import threading
import signal

from constants import responses
from handlers import get, head, post, options
from utilities import get_headers, get_request_line

HOST = '127.0.0.1'
PORT = 1738

RUNNING = True

REQUIRED_HEADERS = ['host', 'content-length']
KEEPALIVE_TIME = 5 # seconds
DISPATCH_DICTIONARY = {'GET': get, 'HEAD': head, 'POST': post, 'OPTIONS': options}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def signal_shutdown(_sig, _frame) -> None:
    global RUNNING
    RUNNING = False

signal.signal(signal.SIGINT, signal_shutdown) # Catch CTRL+C
signal.signal(signal.SIGTERM, signal_shutdown) # Catch kill command

class ParseError(Exception):
    pass

def handle_connection(connection: socket.socket) -> None:
    print('thread started')
    connection.settimeout(KEEPALIVE_TIME)
    with connection as s:
        leftover_buffer = bytearray()
        while True:
            try:
                buffer = bytearray(leftover_buffer)
                header_delimiter = b'\r\n\r\n'

                while header_delimiter not in buffer:
                    chunk = s.recv(1024)
                    if not chunk:
                        if not buffer:
                            print(f'Connection closed cleanly by client')
                            # maybe send a response here too
                            break
                        else:
                            print(f'Connection closed before client sent full header')
                            # error here
                            return
                    buffer.extend(chunk)
                
                if not buffer:
                    break

                head_raw, _, remaining_bytes = buffer.partition(header_delimiter) # partition returns (before, delimiter, after)
                head = head_raw.decode('utf-8')

                try:
                    (method, path, protocol_version), remaining_head = get_request_line(head)
                except ParseError:
                    print('parse error 1')
                    s.sendall(responses.bad_request())
                    break 

                if protocol_version != 'HTTP/1.1':
                    s.sendall(responses.http_version_not_supported())
                    break 

                if method not in DISPATCH_DICTIONARY.keys():
                    s.sendall(responses.not_implemented())
                    break

                try:
                    headers = get_headers(remaining_head)
                except ParseError:
                    s.sendall(responses.bad_request())
                    break

                if not all(k in headers for k in REQUIRED_HEADERS):
                    s.sendall(responses.bad_request())
                    break

                try:
                    content_length = int(headers.get('content-length', 0)) # important, read this from the headers
                except ValueError:
                    print('content length issue')
                    s.sendall(responses.bad_request())
                    break

                body = bytearray(remaining_bytes)

                while len(body) < content_length:
                    bytes_to_read = content_length - len(body)
                    chunk = s.recv(min(bytes_to_read, 4096))
                    if not chunk:
                        print('Connection lost while reading body')
                        return # send failure back ?, maybe internal server error ?
                    body.extend(chunk)
                
                actual_body = body[:content_length]
                leftover_buffer = body[content_length:]

                response = DISPATCH_DICTIONARY[method](path, headers, actual_body)

                s.sendall(response)

                if headers.get('connection', '') == 'close':
                    print('connection closed on request header')
                    break
            except (socket.timeout):
                print(f'connection closed cleanly - idle for {KEEPALIVE_TIME}s')
                break
            except ConnectionResetError:
                print('error: connection forcefully shut down')
                break
    print('thread shut down')

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
    print('Server started')
    main()
    print('Server closed')