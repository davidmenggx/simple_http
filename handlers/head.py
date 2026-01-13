from pathlib import Path
from datetime import datetime, timezone

from constants import responses, MIME_TYPES

BASE_DIR = Path('public').resolve()

def head(path: str, close_connection: bool = False) -> bytes:
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
                        content_type = MIME_TYPES.get(requested_path.suffix, 'application/octet-stream')
                        if close_connection:
                            response = (f'HTTP/1.1 200 OK\r\nDate: {now}\r\nConnection: Close\r\nContent-Length: {len(content)}\r\nContent-Type: {content_type}\r\n\r\n').encode('utf-8')
                        else:
                            response = (f'HTTP/1.1 200 OK\r\nDate: {now}\r\nConnection: Keep-Alive\r\nContent-Length: {len(content)}\r\nContent-Type: {content_type}\r\n\r\n').encode('utf-8')
                        return response
                    except:
                        return responses.internal_server_error()
            except FileNotFoundError:
                return responses.not_found()
        else:
            return responses.not_found()
    else:
        return responses.forbidden()