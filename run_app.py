#!/usr/bin/env python3
import socket
from app import app

def find_free_port():
    """Find a free port starting from 5000"""
    for port in range(5000, 5010):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return 8080  # fallback

if __name__ == '__main__':
    port = find_free_port()
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🌐 Access at: http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)