from app import app
import socket

def find_port():
    for port in range(5000, 5020):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except:
            continue
    return 8080

port = find_port()
print(f"🚀 Starting on http://localhost:{port}")
app.run(host='127.0.0.1', port=port, debug=False)
