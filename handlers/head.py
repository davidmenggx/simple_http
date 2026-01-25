import os
import random
from pathlib import Path
from datetime import datetime, timezone

from utilities import get_etag
from constants import responses, MIME_TYPES

BASE_DIR = Path('public').resolve()

CACHE_TIMES = [10, 30, 60, 600] # Randomly select cache times (in seconds), as an example

def head(path: str, headers: dict[str,str], _: bytes = b'') -> bytes:
    """
    Handler function for HTTP HEAD method, returns response in bytes

    Validates the path

    Formulates response using:
    1) Timestamp of request
    2) Connection status
    3) Content length
    4) Content type
    5) Last modified metadata
    6) ETag

    Possible responses:
    1) 200 OK
    2) 304 Not Modified
    3) 403 Forbidden
    4) 404 Not Found
    5) 500 Internal Server Error
    """
    if path == '/':
        path = 'index.html'
    if path[0] == '/':
        path = path[1:]

    requested_path = (BASE_DIR / path).resolve()

    if not (BASE_DIR in requested_path.parents or BASE_DIR == requested_path): # Prevent path traversal vulnerabilities
        return responses.forbidden()
    
    if not (requested_path.exists() and requested_path.is_file()):
        return responses.not_found()

    try:
        with open(requested_path, 'rb') as f:
            try:
                content = f.read()
                
                now = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

                # Compare ETags, if match, returned Not Modified
                current_etag = get_etag(str(requested_path))
                if current_etag:
                    user_etag = headers.get('if-none-match')
                    if user_etag and user_etag[0] == '"' and user_etag[-1] == '"':
                        user_etag = user_etag[1:-1]
                    if user_etag and user_etag == current_etag:
                        return (f"HTTP/1.1 304 Not Modified\r\nDate: {now}\r\nServer: David's server\r\n\r\n").encode('utf-8')

                # Base response to build on
                response = (f"HTTP/1.1 200 OK\r\nDate: {now}\r\nServer: David's server\r\n")
                
                if headers.get('connection', '') == 'close':
                    response += ('Connection: Close\r\n')
                else:
                    response += ('Connection: Keep-Alive\r\n')
                
                content_type = MIME_TYPES.get(requested_path.suffix, 'application/octet-stream')

                response += (f'Content-Length: {len(content)}\r\nContent-Type: {content_type}\r\n')
                
                last_modified_timestamp = os.stat(requested_path).st_mtime
                modified_utc = datetime.fromtimestamp(last_modified_timestamp, tz=timezone.utc)
                last_modified = modified_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")
                response += (f'Last-Modified: {last_modified}\r\n')
                
                if current_etag:
                    response += (f'ETag: "{current_etag}"\r\n')

                response += (f'Cache-Control: max-age="{random.choice(CACHE_TIMES)}"\r\n')

                response += ('\r\n')
                response = response.encode('utf-8')
                
                return response
            except Exception:
                return responses.internal_server_error()
    except FileNotFoundError:
        return responses.not_found()