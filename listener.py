import http.server
import socketserver

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        print(f"\n*** RECEIVED (possible exfiltration) ***\n{body}\n")
        self.send_response(200)
        self.end_headers()

with socketserver.TCPServer(("localhost", 9999), Handler) as httpd:
    print("Listening on http://localhost:9999 ...")
    httpd.serve_forever()