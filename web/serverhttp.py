import http.server
import threading
import socketserver
from urllib.parse import urlparse
import json

# CORS handler to allow cross-origin requests
class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

# Threaded HTTP server class
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

def run_server():
    # Set up server
    server_address = ('', 8081)  # Host on port 8081
    httpd = ThreadedHTTPServer(server_address, CORSRequestHandler)

    print("Starting server on port 8081...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped with Ctrl+C")

# Run the server in a separate thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()
