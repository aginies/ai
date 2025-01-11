import os
import http.server
import socketserver
from PIL import Image
import io
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

# Directory to scan for images
image_directory = './images'

# Thumbnail size (you can adjust as needed)
thumbnail_size = (150, 150)

# List to store image files (global)
image_files = []

# Function to create a thumbnail of an image
def create_thumbnail(image_path):
    with Image.open(image_path) as img:
        img.thumbnail(thumbnail_size)
        thumb_io = io.BytesIO()
        img.save(thumb_io, format='JPEG')
        thumb_io.seek(0)
        return thumb_io

# Function to update image list when a new image is added
def update_image_list():
    global image_files
    # Get list of image files sorted by modification time (most recent first)
    image_files = sorted(
        [f for f in os.listdir(image_directory) if f.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp'))],
        key=lambda f: os.path.getmtime(os.path.join(image_directory, f)),
        reverse=True
    )

# Custom HTTP request handler
class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # List all images and thumbnails, sorted by date
            images = []
            thumbnails = []
            for filename in image_files:
                # Create thumbnail for the image
                thumb = create_thumbnail(os.path.join(image_directory, filename))
                thumbnails.append((filename, thumb))

            # HTML response with image list and thumbnails, now with better CSS
            html_content = '''
                <html>
                    <head>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                                background-color: #f7f7f7;
                                display: flex;
                                justify-content: center;
                                flex-wrap: wrap;
                            }
                            .gallery-container {
                                display: flex;
                                flex-wrap: wrap;
                                justify-content: center;
                                gap: 20px;
                                width: 100%;
                                max-width: 1200px;
                            }
                            .image-item {
                                background-color: #fff;
                                padding: 10px;
                                border-radius: 8px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                text-align: center;
                                width: 180px;
                                box-sizing: border-box;
                            }
                            .image-item img {
                                width: 100%;
                                border-radius: 4px;
                            }
                            .image-item h3 {
                                font-size: 16px;
                                margin: 10px 0;
                            }
                            .image-item a {
                                text-decoration: none;
                                color: #007BFF;
                            }
                            .image-item a:hover {
                                text-decoration: underline;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="gallery-container">
            '''
            
            for filename, thumb in thumbnails:
                thumb_url = f'/thumbnails/{filename}'
                original_url = f'/images/{filename}'
                html_content += f'''
                    <div class="image-item">
                        <h3>{filename}</h3>
                        <img src="{thumb_url}" alt="{filename}">
                        <br><br>
                        <a href="{original_url}" target="_blank">View Original</a>
                    </div>
                '''
            
            html_content += '''
                        </div>
                    </body>
                </html>
            '''

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

        elif self.path.startswith('/thumbnails/'):
            # Serve the thumbnail image
            image_name = self.path.split('/')[-1]
            image_path = os.path.join(image_directory, image_name)
            if os.path.exists(image_path):
                thumb = create_thumbnail(image_path)
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                self.wfile.write(thumb.read())
            else:
                self.send_response(404)
                self.end_headers()

        elif self.path.startswith('/images/'):
            # Serve the original image
            image_name = self.path.split('/')[-1]
            image_path = os.path.join(image_directory, image_name)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(img_file.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            super().do_GET()

# Watchdog event handler to detect new files
class ImageFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Only process image files
        if event.is_directory:
            return
        elif event.src_path.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp')):
            update_image_list()  # Update the list of images when a new file is created

# Start the file system observer in a separate thread
def start_observer():
    event_handler = ImageFileHandler()
    observer = Observer()
    observer.schedule(event_handler, image_directory, recursive=False)
    observer.start()

# Set the current directory to the directory containing the images
os.chdir(image_directory)

# Initialize the image list and start watching for changes
update_image_list()
observer_thread = threading.Thread(target=start_observer, daemon=True)
observer_thread.start()

# Multi-threaded HTTP server
class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# Start the HTTP server on the specific IP and port
HOST = '10.0.1.38'  # Bind to your local IP
PORT = 8081

Handler = ImageRequestHandler
httpd = ThreadedHTTPServer((HOST, PORT), Handler)

print(f"Serving on {HOST}:{PORT}...")
httpd.serve_forever()

