def get_request_line(request: str) -> tuple[tuple[str, str, str], list[str]]:
    """
    Returns request line as tuple (HTTP method, path, HTTP version) as well as list of headers
    """
    request_line = request.split('\r\n')[0]
    
    if len(request_line.split()) != 3: # Make sure all three elements of the request line (method, URI, version) are present
        raise ValueError
    
    method, path, protocol_version = request_line.split()

    headers = request_line = request.split('\r\n')[1:]

    return ((method, path, protocol_version), headers)