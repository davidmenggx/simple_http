import os
import hashlib

def get_etag(requested_path: str) -> str:
    """Generates ETag based on last modified metadata using SHA256 hash"""
    try:
        last_modified = os.stat(requested_path).st_mtime
        sha256_hash = hashlib.sha256()
        sha256_hash.update(str(last_modified).encode('utf-8'))
        return sha256_hash.hexdigest()
    except:
        return ''