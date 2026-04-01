import http.server
import socketserver
import json
import os
import mimetypes
from database import TaskDatabase

class TaskRequestHandler(http.server.BaseHTTPRequestHandler):
  
    db = TaskDatabase()

    def _send_response(self, data, status=200):
        """Internal helper to simplify sending JSON responses."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _serve_files(self):
        """Internal helper to serve Frontend files (HTML, CSS, JS, PNG)."""
        # Logic to map URL path to files in our current folder
        path = self.path if self.path != '/' else '/index.html'
        file_path = os.path.join(os.getcwd(), path.lstrip('/'))

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            mime_type, _ = mimetypes.guess_type(file_path)
            self.send_header('Content-Type', mime_type or 'text/plain')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File not found")

    def do_OPTIONS(self):
        """Allows browsers to perform pre-flight checks (CORS)."""
        self._send_response({"status": "OK"})

    def do_GET(self):
        """Handling 'Read' requests from the browser."""
        if self.path == '/api/tasks':
            tasks = self.db.get_all_tasks()
            response = [t.to_dict() for t in tasks]
            self._send_response(response)
        else:
            self._serve_files()

    def do_POST(self):
        """Handling 'Create' requests from the browser."""
        if self.path == '/api/tasks':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode()
            data = json.loads(body)
            
            if 'title' in data:
                self.db.add_new_task(data['title'])
                self._send_response({"message": "Successfully created!"}, 201)

    def do_PUT(self):
        """Handling 'Update' requests from the browser."""
        if self.path.startswith('/api/tasks/'):
            task_id = int(self.path.split('/')[-1])
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode())
            
            self.db.update_status(task_id, data.get('completed', False))
            self._send_response({"message": "Successfully updated!"})

    def do_DELETE(self):
        """Handling 'Delete' requests from the browser."""
        if self.path.startswith('/api/tasks/'):
            task_id = int(self.path.split('/')[-1])
            self.db.remove_task(task_id)
            self._send_response({"message": "Successfully deleted!", "id": task_id})

class TaskApp:
    """This class represents the whole application and handles the server start."""
    def __init__(self, port=8000):
        self.port = port

    def start(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        socketserver.TCPServer.allow_reuse_address = True
        
        with socketserver.TCPServer(("", self.port), TaskRequestHandler) as httpd:
            print(f"🚀 TaskFlow Server is running at: http://localhost:{self.port}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Server stopped.")
                httpd.shutdown()

if __name__ == "__main__":
    # Create the App Object and start the server
    app = TaskApp(port=8000)
    app.start()
