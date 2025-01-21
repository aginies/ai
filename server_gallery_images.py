import os
import signal
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from jinja2 import Template
from urllib.parse import urlparse, parse_qs
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Directory to watch
IMAGES_DIR = "/home/aginies/comfyUI/output"
THUMB_SIZE = 200  # Parameter for thumbnail size in pixels
IMAGES_PER_PAGE = 100  # Number of images per page

# HTML template for the webpage
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Generated Images Gallery</title>
    <style>
       body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #121212; /* Dark mode background */
            color: #e0e0e0; /* Dark mode text color */
        }
        .gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            padding: 20px;
        }
        .gallery-item {
            text-align: center;
        }
        .gallery img {
            width: {{ thumb_size }}px;
            height: auto;
            border: 1px solid #444; /* Dark mode border color */
            border-radius: 5px;
            cursor: pointer;
        }
        .gallery-item span {
            display: block;
            margin-top: 5px;
            font-size: 14px;
            color: #e0e0e0; /* Dark mode text color */
        }
        .delete-button {
            display: block;
            margin-top: 5px;
            background-color: #ff4d4d;
            color: white;
            border: none;
            padding: 3px 6px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        .pagination {
            text-align: center;
            margin-top: 20px;
        }
        .pagination a, .pagination span {
            display: inline-block;
            padding: 8px 16px;
            margin: 4px;
            border-radius: 5px;
            background-color: #333; /* Dark mode background for pagination links */
            color: white;
            text-decoration: none;
            cursor: pointer;
        }
        .pagination a:hover {
            background-color: #666; /* Dark mode hover color for pagination links */
        }
        .pagination .active {
            background-color: #4CAF50;
            color: white;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal img {
            max-width: 90%;
            max-height: 80%;
        }
        .modal .close {
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            font-size: 24px;
            cursor: pointer;
        }
        .modal .nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            font-size: 36px;
            color: white;
            cursor: pointer;
            user-select: none;
        }
        .modal .prev {
            left: 20px;
        }
        .modal .next {
            right: 20px;
        }
        #modalImage {
            position: absolute;
            max-width: 90%;
            max-height: 90%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            object-fit: contain;
    </style>
</head>
<body>
    <h1 style="text-align:center;">AI Generated Images Gallery</h1>
    <div class="gallery">
        {% for image in images %}
        <div class="gallery-item">
            <img src="{{ image.path }}" alt="{{ image.name }}" onclick="openModal({{ loop.index0 }})">
            <span>{{ image.name }}</span>
            <button class="delete-button" onclick="deleteImage('{{ image.name }}')">Delete</button>
        </div>
        {% endfor %}
    </div>
    <div class="pagination">
        {% if current_page > 1 %}
        <a href="/?page={{ current_page - 1 }}">Previous</a>
        {% endif %}
        <span class="active">{{ current_page }} of {{ total_pages }}</span>
        {% if current_page < total_pages %}
        <a href="/?page={{ current_page + 1 }}">Next</a>
        {% endif %}
    </div>

    <!-- Modal for fullscreen view -->
    <div class="modal" id="imageModal">
        <span class="close" onclick="closeModal()">&times;</span>
        <span class="nav prev" onclick="prevImage()">&#10094;</span>
        <span class="nav next" onclick="nextImage()">&#10095;</span>
        <img id="modalImage" src="" alt="">
    </div>

    <script>
        let images = {{ images | tojson }};
        let currentIndex = 0;
        document.addEventListener('keydown', function(event) {
            const modal = document.getElementById('imageModal');
            if (modal.style.display === 'block') { // Check if modal is open
                switch (event.key) {
                    case 'Escape':
                        closeModal();
                        break;
                    case 'ArrowLeft':
                        prevImage();
                        break;
                    case 'ArrowRight':
                        nextImage();
                        break;
                    default:
                        break;
                }
            }
        });

        function openModal(index) {
            currentIndex = index;
            const modal = document.getElementById('imageModal');
            const modalImage = document.getElementById('modalImage');
            modal.style.display = 'block';
            modalImage.src = images[currentIndex].path;
        }

        function closeModal() {
            const modal = document.getElementById('imageModal');
            modal.style.display = 'none';
        }

        function prevImage() {
            if (currentIndex > 0) {
                currentIndex--;
                document.getElementById('modalImage').src = images[currentIndex].path;
            }
        }

        function nextImage() {
            if (currentIndex < images.length - 1) {
                currentIndex++;
                document.getElementById('modalImage').src = images[currentIndex].path;
            }
        }

        function deleteImage(imageName) {
            if (confirm('Are you sure you want to delete this image?')) {
                var page = {{ current_page }};
                fetch(`/delete?name=${encodeURIComponent(imageName)}&page=${encodeURIComponent(page)}`, { method: 'POST' })
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
</body>
</html>
"""

# Generate the HTML file based on the current images in the directory and page number
def generate_html(page=1):
    base_url_path = os.path.basename(IMAGES_DIR)
    all_images = [
        {
            "path": f"{base_url_path}/{img}",  # Use the direct path
            "name": img,
            "mtime": os.path.getmtime(os.path.join(IMAGES_DIR, img))
        }
        for img in os.listdir(IMAGES_DIR)
        if img.lower().endswith((".png", ".jpg", ".jpeg", ".gif")) and os.path.getsize(os.path.join(IMAGES_DIR, img)) > 0
    ]
    all_images.sort(key=lambda x: x["mtime"], reverse=True)  # Sort by modification time, descending

    total_pages = (len(all_images) + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE  # Ceiling division
    page = max(1, min(page, total_pages))  # Clamp page number between 1 and total_pages

    start_index = (page - 1) * IMAGES_PER_PAGE
    end_index = min(start_index + IMAGES_PER_PAGE, len(all_images))
    images_for_page = all_images[start_index:end_index]

    template = Template(HTML_TEMPLATE)
    rendered_html = template.render(
        images=images_for_page,
        thumb_size=THUMB_SIZE,
        current_page=page,
        total_pages=total_pages
    )

    with open("index.html", "w") as f:
        f.write(rendered_html)

# HTTP handler class
class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        page = int(query.get("page", [1])[0])
        generate_html(page)
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)

        if parsed_path.path == "/delete":
            query = parse_qs(parsed_path.query)
            page = int(query.get("page", [1])[0])
            if "name" in query:
                image_name = query["name"][0]
                image_path = os.path.join(IMAGES_DIR, image_name)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    generate_html(page)  # Regenerate HTML for the current page
                    self.send_response(200)
                    self.end_headers()
                    return
        self.send_response(400)
        self.end_headers()

# Watchdog handler to monitor changes in the directory
class ImageChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.event_type in ["created", "deleted", "modified"]:
            generate_html()  # Regenerate HTML for page 1

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
