import os
import signal
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from jinja2 import Template
from urllib.parse import urlparse, parse_qs
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Directory to watch
IMAGES_DIR = "/home/aginies/LocalAI/images"
THUMB_SIZE = 200  # Parameter for thumbnail size in pixels

# HTML template for the webpage
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Generated Images Gallery</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        .gallery { display: flex; flex-wrap: wrap; gap: 10px; padding: 20px; }
        .gallery-item { text-align: center; }
        .gallery img { width: {{ thumb_size }}px; height: auto; border: 1px solid #ccc; border-radius: 5px; cursor: pointer; }
        .gallery-item span { display: block; margin-top: 5px; font-size: 14px; color: #333; }
        .delete-button { display: block; margin-top: 5px; background-color: #ff4d4d; color: white; border: none; padding: 3px 6px; border-radius: 5px; cursor: pointer; font-size: 12px; }
    </style>
    <script>
        function deleteImage(imageName) {
            if (confirm('Are you sure you want to delete this image?')) {
                fetch(`/delete?name=${encodeURIComponent(imageName)}`, { method: 'POST' })
                    .then(response => {
                        if (response.ok) {
                            window.location.reload();
                        } else {
                            alert("Failed to delete image");
                        }
                    });
            }
        }
    </script>
</head>
<body>
    <h1 style="text-align:center;">Image Gallery</h1>
    <div class="gallery">
        {% for image in images %}
        <div class="gallery-item">
            <a href="{{ image.path }}" target="_blank">
                <img src="{{ image.path }}" alt="{{ image.name }}">
            </a>
            <span>{{ image.name }}</span>
            <button class="delete-button" onclick="deleteImage('{{ image.name }}')">Delete</button>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# Generate the HTML file based on the current images in the directory
def generate_html():
    images = [
        {
            "path": f"/images/{img}",
            "name": img,
            "mtime": os.path.getmtime(os.path.join(IMAGES_DIR, img))
        }
        for img in os.listdir(IMAGES_DIR)
        if img.lower().endswith((".png", ".jpg", ".jpeg", ".gif")) and os.path.getsize(os.path.join(IMAGES_DIR, img)) > 0
    ]
    images.sort(key=lambda x: x["mtime"], reverse=True)  # Sort by modification time, descending
    template = Template(HTML_TEMPLATE)
    rendered_html = template.render(images=images, thumb_size=THUMB_SIZE)

    with open("index.html", "w") as f:
        f.write(rendered_html)

# HTTP handler class
class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/delete":
            query = parse_qs(parsed_path.query)
            if "name" in query:
                image_name = query["name"][0]
                image_path = os.path.join(IMAGES_DIR, image_name)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    generate_html()
                    self.send_response(200)
                    self.end_headers()
                    return
        self.send_response(400)
        self.end_headers()

# Watchdog handler to monitor changes in the directory
class ImageChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.event_type in ["created", "deleted", "modified"]:
            generate_html()

# HTTP server in a thread
class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.server = HTTPServer(("", 8000), CustomHandler)
        self.daemon = True  # Ensures thread terminates with the main program

    def run(self):
        print("Starting HTTP server on http://localhost:8000... Press Ctrl+C to stop.")
        try:
            self.server.serve_forever()
        except Exception:
            pass  # Allow shutdown to proceed

    def stop(self):
        print("Shutting down HTTP server...")
        self.server.shutdown()
        self.server.server_close()

# Main program
if __name__ == "__main__":
    # Ensure the HTML is up-to-date at the start
    generate_html()

    # Start the HTTP server in a separate thread
    server_thread = ServerThread()
    server_thread.start()

    # Set up the observer to watch for changes in the images directory
    observer = Observer()
    observer.schedule(ImageChangeHandler(), path=IMAGES_DIR, recursive=False)
    observer.start()

    # Graceful shutdown handler
    def shutdown_handler(signum, frame):
        print("\nStopping observer and HTTP server...")
        observer.stop()
        observer.join()
        server_thread.stop()
        print("Stopped.")
        exit(0)

    # Capture Ctrl+C
    signal.signal(signal.SIGINT, shutdown_handler)

    # Wait for termination signal
    signal.pause()

