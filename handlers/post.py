from pathlib import Path
from datetime import datetime, timezone

from utilities import get_etag
from constants import responses, MIME_TYPES

BASE_DIR = Path('public').resolve()
API_DIR = Path('public/api').resolve()

def post(path: str, headers: dict[str, str], body: bytes = b'') -> bytes:
    """
    Handler function for HTTP POST method, returns response in bytes

    Validates the path

    Attempts to write request body to specified path

    Formulates response using:
    1) Timestamp of request
    2) Connection status
    3) Content location
    4) Content type
    5) ETag

    Possible responses:
    1) 200 OK
    2) 403 Forbidden
    3) 404 Not Found
    4) 405 Method Not Allowed
    5) 500 Internal Server Error
    """
    if path == '/':
        path = 'index.html'
    elif path[0] == '/':
        path = path[1:]

    requested_path = (BASE_DIR / path).resolve()

    if not (BASE_DIR in requested_path.parents or BASE_DIR == requested_path): # Prevent path traversal vulnerabilities
        return responses.forbidden()
    
    if not (API_DIR in requested_path.parents or API_DIR == requested_path): # Only files in public/api/ can be accessed
        return responses.method_not_allowed()
    
    if not (requested_path.exists() and requested_path.is_file()):
        return responses.not_found()

    try:
        with open(requested_path, 'ab') as f:
            try:
                f.write(body)

                f.flush()

                etag = get_etag(str(requested_path))

                now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

                # Base response to build on
                response = (
                    f'HTTP/1.1 200 OK\r\n'
                    f"Server: David's server\r\n"
                    f'Date: {now}\r\n'
                    f'Location: {path}\r\n'
                    f'Content-Type: {MIME_TYPES.get(requested_path.suffix, 'application/octet-stream')}\r\n'
                    )
                
                if etag:
                    response += f'ETag: {etag}\r\n'
                
                if headers.get('connection', '') == 'close':
                    response += ('Connection: Close\r\n')
                else:
                    response += ('Connection: Keep-Alive\r\n')
                
                response += ('\r\n')
                
                return response.encode('utf-8')
            except Exception:
                return responses.internal_server_error()
    except FileNotFoundError:
        return responses.not_found()