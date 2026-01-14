from pathlib import Path
from datetime import datetime, timezone

from utilities import get_etag
from constants import responses, MIME_TYPES

BASE_DIR = Path('public').resolve()
API_DIR = Path('public/api').resolve()

def post(path: str, headers: dict[str, str], body: bytes = b'') -> bytes:
    if path[0] == '/':
        path = path[1:]

    requested_path = (BASE_DIR / path).resolve()

    if BASE_DIR in requested_path.parents or BASE_DIR == requested_path:
        if API_DIR in requested_path.parents or API_DIR == requested_path:
            if requested_path.exists() and requested_path.is_file():
                try:
                    with open(requested_path, 'ab') as f:
                        try:
                            f.write(body)
                            f.write(('\r\n').encode('utf-8'))

                            f.flush()

                            with open(requested_path, 'rb') as f:
                                content = f.read()
                            etag = get_etag(content)

                            now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

                            response = (
                                f'HTTP/1.1 201 Created\r\n'
                                f"Server: David's server\r\n"
                                f'Date: {now}\r\n'
                                f'Location: {path}\r\n'
                                f'Content-Type: {MIME_TYPES.get(requested_path.suffix, 'application/octet-stream')}\r\n'
                                f'ETag: {etag}\r\n'
                                )
                            
                            if headers.get('connection', '') == 'close':
                                response += (f'Connection: Close\r\n')
                            else:
                                response += (f'Connection: Keep-Alive\r\n')

                            response += ('\r\n')
                            
                            return response.encode('utf-8')
                        except:
                            return responses.internal_server_error()
                except FileNotFoundError:
                    return responses.not_found()
            else:
                return responses.not_found()
        else:
            return responses.method_not_allowed()
    else:
        return responses.forbidden()