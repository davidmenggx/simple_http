# simple_http
Multi-threaded HTTP server built using only the Python standard library
## Features
- HTTP/1.1 subset
- Serves Static Files: Delivers HTML, CSS, JS, image, json, txt, and other data formats
- Support for IPv4 connections via TCP
- Handles multiple client requests simultaneously with multi-threading
- ***HTTP Methods***: Support for **`GET`**, **`POST`** (subset), **`OPTIONS`**, and **`HEAD`** methods
- ***HTTP Headers***: Support for `Content-Type`, `Content-Length`, **`Connection`**, **`ETag`**, **`If-None-Match`**, `Date`, `Last-Modified`, `Host`, and `User-Agent` headers
- ***HTTP Responses***: Support for `200 OK`, `204 No Content`, `304 Not Modified`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `405 Method Not Allowed`, `500 Internal Server Error`, `501 Not Implemented`, and `505 HTTP Version Not Supported` messages
    - Correct error handling for *path traversal vulnerabilities* (`403 Forbidden`) and *permissions for dynamic files* (`405 Method Not Allowed`)
    - Correctly returns `304 Not Modified` if *strong ETag* is provided and validated
- Persistent connections with keep-alive
## Get Started
With Python 3.x
1. **Clone this repository:**
```bash
git clone https://github.com/davidmenggx/simple_http && cd simple_http
```
2. **Run the server:**
```bash
python3 server.py
```
**Optional: Specify port number, keepalive time (seconds), and verbose**<br>
Defaults to port 8080, 5 seconds keep-alive, no logging
```bash
python server.py --port 5678 --keepalive 30 -v
```
## Usage
Base directory is `public/`<br><br>
Dynamic assets in `api/` allow `POST`, `GET`, `OPTIONS`, `HEAD`<br>
All other static assets allow `GET`, `OPTIONS`, `HEAD`
```plaintext
public/
├── api/
│   ├── comments.json
│   └── public_file.txt
├── data /
│   ├── users.json
│   └── videos.json
├── images /
│   └── img1.jpg
├── index.html
├── script.js
└── styles.css
```
## Testing
Fetch `index.html` (using default port 8080):
```bash
curl http://localhost:8080/
```
Visit the front page: <http://localhost:8080> (or the port you specified)<br><br><br>
Make a post to `api/public_file.txt`:
```bash
curl -i -X POST -d "Hello from GitHub" http://localhost:8080/api/public_file.txt
```
Now read `api/public_file.txt`:
```bash
curl -i http://localhost:8080/api/public_file.txt
```

