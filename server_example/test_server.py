"""
Simple HTTP server for testing updates locally.
Serves the updates.json file and update packages.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 8000

class UpdateServerHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve update files with proper headers."""
    
    def end_headers(self):
        # Add CORS headers for testing
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the test server."""
    
    # Change to the server_example directory
    server_dir = Path(__file__).parent
    os.chdir(server_dir)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           Alpha Update Agent - Test Update Server           ║
╚══════════════════════════════════════════════════════════════╝

Serving update files from: {server_dir}
Server URL: http://localhost:{PORT}/

Available endpoints:
  - http://localhost:{PORT}/updates.json
  - http://localhost:{PORT}/updates_1.0.2.json
  - http://localhost:{PORT}/updates/1.0.1.zip
  - http://localhost:{PORT}/updates/1.0.2.zip

To test the update system:
  1. Make sure your agent's config.json has:
     "update_server": "http://localhost:{PORT}/updates.json"
  
  2. Run the agent:
     python main.py check

Press Ctrl+C to stop the server.
    """)
    
    try:
        with socketserver.TCPServer(("", PORT), UpdateServerHandler) as httpd:
            print(f"Server started on port {PORT}\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"\nError: Port {PORT} is already in use.")
            print("Please stop the other server or change the PORT variable.")
            sys.exit(1)
        else:
            raise


if __name__ == "__main__":
    main()

