#!/usr/bin/env python3
# serve_html.py - Simple HTTP server to serve HTML files

import http.server
import socketserver
import os
import webbrowser
from urllib.parse import urlparse

# Configuration
PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, businessapikey, Accept, Origin')
        self.send_header('Access-Control-Expose-Headers', 'Content-Type, Authorization, businessapikey')
        self.send_header('Access-Control-Max-Age', '3600')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()

def run_server():
    # Change to the directory containing the HTML files
    os.chdir(DIRECTORY)
    
    # Create the server
    handler = MyHttpRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Server started at http://localhost:{PORT}")
    print(f"Serving files from: {DIRECTORY}")
    print("Press Ctrl+C to stop the server")
    
    # Open the browser to the server
    webbrowser.open(f"http://localhost:{PORT}/llm.html")
    
    # Start the server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()