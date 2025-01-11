from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Define a ThreadingHTTPServer class
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == "__main__":
    port = 8081
    server_address = ("", port)
    # Create the server instance
    httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serving HTTP on port {port}...")
    try:
    # Start the server
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        httpd.server_close()

