import signal
import socket
import logging
import argparse
import threading

from constants import responses
from handlers import get, head, post, options
from utilities import get_headers, get_request_line

# Parse command line arguments
parser = argparse.ArgumentParser(description="Configs for simple HTTP server")
parser.add_argument('-p', '--port', type=int, default=8080, help='Port for server to run on')
parser.add_argument('-k', '--keepalive', type=int, default=5, help='Keepalive time in seconds for each connection')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Enable verbose mode for workers')
parser.add_argument('-d', '--discovery', type=int, default=49152, help='Discovery port for reverse proxy')
args = parser.parse_args()

# Validate command line arguments:
if not (0 <= args.port <= 65535):
    raise ValueError(f'FATAL: specified port {args.port} does not exist!')

if not (0 <= args.discovery <= 65535):
    raise ValueError(f'FATAL: specified discovery port {args.discovery} does not exist!')

if args.port == args.discovery:
    raise ValueError(f'FATAL: Server and discovery port cannot be the same! Currently both {args.port}')

# Server settings and constants
HOST = '127.0.0.1'
PORT = args.port
DISCOVERY_PORT = args.discovery

KEEPALIVE_TIME = args.keepalive

HEADER_DELIMITER = b'\r\n\r\n'

DISPATCH_DICTIONARY = {'GET': get, 'HEAD': head, 'POST': post, 'OPTIONS': options} # Dictionary to map supported methods to appropriate handlers

# Create logger
LOGGER = logging.getLogger("simple_http")
_console_handler = logging.StreamHandler()
_file_handler = logging.FileHandler('server.log')
if args.verbose:
    LOGGER.setLevel(logging.DEBUG)
    _console_handler.setLevel(logging.DEBUG)
    _file_handler.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.WARNING)
    _console_handler.setLevel(logging.WARNING)
    _file_handler.setLevel(logging.WARNING)

_log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_date_format = "%Y-%m-%dT%H:%M:%SZ" # ISO 8601 style
_formatter = logging.Formatter(fmt=_log_format, datefmt=_date_format)
_console_handler.setFormatter(_formatter)
_file_handler.setFormatter(_formatter)

LOGGER.addHandler(_console_handler)
LOGGER.addHandler(_file_handler)

# Shut the server down
RUNNING = True
def signal_shutdown(_sig, _frame) -> None:
    """Shut down server"""
    global RUNNING
    RUNNING = False
signal.signal(signal.SIGINT, signal_shutdown) # Catch CTRL+C
signal.signal(signal.SIGTERM, signal_shutdown) # Catch kill command

# Server connections
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def handle_connection(connection: socket.socket) -> None:
    """
    Target function for worker threads to handle request

    Reads message from socket and parses out request line, headers, and body

    If any parsing fails, immediately return 400 Bad Request

    Validates HTTP version, required headers, and supported methods

    Sends the appropriate response based on HTTP method

    Keeps connection alive, unless otherwise specified by client
    """
    LOGGER.debug('Thread started')
    connection.settimeout(KEEPALIVE_TIME)
    with connection as s:
        leftover_buffer = bytearray() # In case buffer contains part of two messages, split them up
        while True: # Keep the connection alive, unless otherwise specified by client
            try:
                buffer = bytearray(leftover_buffer)

                while HEADER_DELIMITER not in buffer:
                    chunk = s.recv(1024)
                    if not chunk:
                        if not buffer:
                            LOGGER.debug('Connection closed cleanly by client')
                            break
                        else:
                            LOGGER.critical('Connection closed before client sent full header')
                            return
                    buffer.extend(chunk)
                
                if not buffer:
                    break

                head_raw, _, remaining_bytes = buffer.partition(HEADER_DELIMITER) # Partition returns (before, delimiter, after)
                head = head_raw.decode('utf-8')

                try:
                    (method, path, protocol_version), remaining_head = get_request_line(head)
                except ValueError:
                    LOGGER.warning('Error parsing request line - bad request')
                    s.sendall(responses.bad_request())
                    break 

                if protocol_version != 'HTTP/1.1':
                    LOGGER.warning('Incorrect HTTP version, must use HTTP/1.1 - bad request')
                    s.sendall(responses.http_version_not_supported())
                    break

                if method not in DISPATCH_DICTIONARY.keys(): # Fails fast in case method isn't supported
                    LOGGER.warning(f'Method {method} not supported - bad request')
                    s.sendall(responses.not_implemented())
                    break

                try:
                    headers = get_headers(remaining_head)
                except ValueError:
                    LOGGER.warning('Failed to parse headers - bad request')
                    s.sendall(responses.bad_request())
                    break

                try:
                    content_length = int(headers.get('content-length', 0)) # Important, read this from the headers
                except ValueError:
                    LOGGER.warning('Failed to fetch content length - bad request')
                    s.sendall(responses.bad_request())
                    break

                body = bytearray(remaining_bytes)

                while len(body) < content_length:
                    bytes_to_read = content_length - len(body)
                    chunk = s.recv(min(bytes_to_read, 4096))
                    if not chunk:
                        LOGGER.critical('Failed reading request body')
                        s.sendall(responses.internal_server_error())
                        return
                    body.extend(chunk)
                
                leftover_buffer = body[content_length:] # Leftover buffer if multiple messages loaded
                body = body[:content_length]

                response = DISPATCH_DICTIONARY[method](path, headers, body) # Call the appropriate handler for the HTTP method

                s.sendall(response)

                if headers.get('connection', '') == 'close': # Close connection if specified by client
                    LOGGER.debug('Connection closed by client, specified in header')
                    break
            except ConnectionResetError:
                break
            except (socket.timeout):
                LOGGER.debug(f'Connection closed naturally, idle for {KEEPALIVE_TIME} seconds')
                break
    LOGGER.debug('Thread closed')

def main() -> None:
    """
    Main server loop

    Listens to new connections on HOST:PORT

    Spawns worker thread to handle request
    """

    LOGGER.debug(f'Listening on port {PORT}')

    with sock as s:
        s.bind((HOST, PORT))
        s.listen()
        s.settimeout(1.0) # Timeout is needed since accept is blocking
        while RUNNING:
            try:
                conn, _ = s.accept()
            except socket.timeout:
                continue

            connection_worker = threading.Thread(target=handle_connection, args=(conn,), daemon=True) # Daemon so the workers don't prevent main server shutdown
            connection_worker.start()

if __name__ == '__main__':
    try: # Attempt to ping the reverse proxy's discovery port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, DISCOVERY_PORT))
            s.sendall((f'{HOST},{PORT}\r\n').encode('utf-8'))
    except Exception:
        pass

    LOGGER.debug('Server started')

    main()
    
    LOGGER.debug('Server closed')