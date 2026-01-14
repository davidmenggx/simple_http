from pathlib import Path
from datetime import datetime, timezone

from constants import responses

BASE_DIR = Path('public').resolve()
API_DIR = Path('public/api').resolve()


def options(path: str, headers: dict[str,str], body: bytes = b'') -> bytes:
    """
    Handler function for HTTP OPTIONS method, returns response in bytes

    Validates the path

    Formulates response based on resource category (static or API)

    Possible responses:
    1) 204 No Content
    2) 403 Forbidden
    3) 404 Not Found
    4) 500 Internal Server Error
    """
    if path[0] == '/':
        path = path[1:]

    requested_path = (BASE_DIR / path).resolve()

    if not (BASE_DIR in requested_path.parents or BASE_DIR == requested_path):
        return responses.forbidden()
    
    if not (requested_path.exists() and requested_path.is_file()):
        return responses.not_found()

    try:
        now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        response = (f"HTTP/1.1 204 No Content\r\n")

        if API_DIR in requested_path.parents or API_DIR == requested_path:
            response += (f'Allow: OPTIONS, GET, HEAD, POST\r\n')
        else:
            response += (f'Allow: OPTIONS, GET, HEAD\r\n')
        
        response += (f"Date: {now}\r\nServer: David's server\r\n")
        
        if headers.get('connection', '') == 'close':
            response += (f'Connection: Close\r\n')
        else:
            response += (f'Connection: Keep-Alive\r\n')
        
        response += (f'\r\n')
        response = response.encode('utf-8')
        
        return response
    except:
        return responses.internal_server_error()