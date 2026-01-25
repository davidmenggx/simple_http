from datetime import datetime, timezone

def _format_error_response(status_line: str) -> bytes:
    """Template for standard server responses (errors)"""
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    return (f"{status_line}\r\nServer: David's server\r\nDate: {now}\r\nContent-Length: 0\r\n\r\n").encode('utf-8')

def bad_request(): return _format_error_response('HTTP/1.1 400 Bad Request')

def forbidden(): return _format_error_response('HTTP/1.1 403 Forbidden')

def not_found(): return _format_error_response('HTTP/1.1 404 Not Found')

def method_not_allowed(): return _format_error_response('HTTP/1.1 405 Method Not Allowed')

def internal_server_error(): return _format_error_response('HTTP/1.1 500 Internal Server Error')

def not_implemented(): return _format_error_response('HTTP/1.1 501 Not Implemented')

def http_version_not_supported(): return _format_error_response('HTTP/1.1 505 HTTP Version Not Supported')