import os
from pathlib import Path
from datetime import datetime, timezone

from utilities import get_etag
from constants import responses, MIME_TYPES

BASE_DIR = Path('public').resolve()

def get(path: str, headers: dict[str,str], body: bytes = b'') -> bytes:
    if path[0] == '/':
        path = path[1:]

    requested_path = (BASE_DIR / path).resolve()

    if BASE_DIR in requested_path.parents or BASE_DIR == requested_path:
        if requested_path.exists() and requested_path.is_file():
            try:
                with open(requested_path, 'rb') as f:
                    try:
                        content = f.read()

                        now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
                        
                        current_etag = get_etag(str(requested_path))
                        user_etag = headers.get('if-none-match')
                        if user_etag and user_etag[1:-1] == current_etag:
                            return (f"HTTP/1.1 304 Not Modified\r\nDate: {now}\r\nServer: David's server\r\n\r\n").encode('utf-8')

                        response = (f"HTTP/1.1 200 OK\r\nDate: {now}\r\nDavid's server\r\n")
                        
                        if headers.get('connection', '') == 'close':
                            response += (f'Connection: Close\r\n')
                        else:
                            response += (f'Connection: Keep-Alive\r\n')
                        
                        content_type = MIME_TYPES.get(requested_path.suffix, 'application/octet-stream')
                        response += (f'Content-Length: {len(content)}\r\nContent-Type: {content_type}\r\n')

                        last_modified_timestamp = os.stat(requested_path).st_mtime
                        modified_utc = datetime.fromtimestamp(last_modified_timestamp, tz=timezone.utc)
                        last_modified = modified_utc.strftime("%A, %d %B %Y %H:%M:%S GMT")

                        response += (f'Last-Modified: {last_modified}\r\n')
                        
                        response += (f'ETag: "{current_etag}"\r\n')

                        response += (f'\r\n')
                        response = response.encode('utf-8') + content
                        
                        return response
                    except:
                        return responses.internal_server_error()
            except FileNotFoundError:
                return responses.not_found()
        else:
            return responses.not_found()
    else:
        return responses.forbidden()