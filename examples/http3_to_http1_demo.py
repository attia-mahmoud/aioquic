#!/usr/bin/env python3
"""
HTTP/3 to HTTP/1 Demo Driver

This file demonstrates how to use an HTTP/3 client to communicate with
an HTTP/1 server through a proxy that handles the protocol conversion.
The client speaks HTTP/3, the server speaks HTTP/1, and the proxy
handles the translation between them.
"""

import logging
import threading
import time
import http.server
import socketserver
import urllib.request
import urllib.parse
import urllib.error
import signal
import sys

# Import our HTTP/3 client implementation
from simple_http3_client import connect_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("http3_to_http1_demo")

# Global server instance for cleanup
_http_server = None


class SimpleHttp1Handler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP/1.1 server handler that responds to requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        logger.info(f"📥 HTTP/1 server received GET request: {self.path}")
        
        if self.path == "/":
            # Serve homepage
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Server', 'SimpleHTTP1/1.0')
            self.send_header('X-Powered-By', 'Python http.server')
            self.end_headers()
            
            response_body = """
            <html>
            <head><title>HTTP/1.1 Server</title></head>
            <body>
                <h1>HTTP/1.1 Server</h1>
                <p>This is a simple HTTP/1.1 server that receives requests from an HTTP/3 client through a proxy.</p>
                <p>Request path: {}</p>
                <p>User-Agent: {}</p>
            </body>
            </html>
            """.format(self.path, self.headers.get('User-Agent', 'Unknown'))
            
            self.wfile.write(response_body.encode('utf-8'))
            logger.info("✅ HTTP/1 server sent homepage response")
            
        elif self.path == "/api/status":
            # Serve JSON status
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Server', 'SimpleHTTP1/1.0')
            self.send_header('X-Powered-By', 'Python http.server')
            self.end_headers()
            
            import json
            status_data = {
                "status": "ok",
                "server": "HTTP/1.1",
                "message": "Server is running",
                "timestamp": time.time()
            }
            
            response_body = json.dumps(status_data, indent=2)
            self.wfile.write(response_body.encode('utf-8'))
            logger.info("✅ HTTP/1 server sent JSON status response")
            
        else:
            # 404 for unknown paths
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Server', 'SimpleHTTP1/1.0')
            self.end_headers()
            
            self.wfile.write(b"Not Found")
            logger.warning(f"❌ HTTP/1 server sent 404 for: {self.path}")
    
    def do_POST(self):
        """Handle POST requests."""
        logger.info(f"📥 HTTP/1 server received POST request: {self.path}")
        
        if self.path == "/api/echo":
            # Echo the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Server', 'SimpleHTTP1/1.0')
            self.send_header('X-Powered-By', 'Python http.server')
            self.send_header('Content-Length', str(len(post_data)))
            self.end_headers()
            
            self.wfile.write(post_data)
            logger.info(f"✅ HTTP/1 server echoed back {len(post_data)} bytes")
            
        else:
            # 404 for unknown paths
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Server', 'SimpleHTTP1/1.0')
            self.end_headers()
            
            self.wfile.write(b"Not Found")
            logger.warning(f"❌ HTTP/1 server sent 404 for: {self.path}")
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"HTTP/1 Server: {format % args}")


def run_http1_server(host="localhost", port=8443):
    """Run the HTTP/1 server in a background thread."""
    global _http_server
    logger.info(f"🚀 Starting HTTP/1 server on {host}:{port}")
    
    try:
        _http_server = socketserver.TCPServer((host, port), SimpleHttp1Handler)
        _http_server.allow_reuse_address = True  # Allow reuse of the address
        logger.info(f"✅ HTTP/1 server is running on {host}:{port}")
        _http_server.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"❌ Port {port} is already in use. Please stop any service using this port.")
            logger.error("💡 You can kill the process using: sudo lsof -ti:8443 | xargs kill -9")
        else:
            logger.error(f"❌ Failed to start HTTP/1 server: {e}")
        raise


def stop_http1_server():
    """Stop the HTTP/1 server gracefully."""
    global _http_server
    if _http_server:
        logger.info("🛑 Stopping HTTP/1 server...")
        _http_server.shutdown()
        _http_server.server_close()
        logger.info("✅ HTTP/1 server stopped")


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    logger.info("🛑 Received interrupt signal, shutting down...")
    stop_http1_server()
    sys.exit(0)


def test_http1_server_directly():
    """Test the HTTP/1 server directly to make sure it's working."""
    logger.info("🧪 Testing HTTP/1 server directly...")
    
    try:
        # Test GET request
        response = urllib.request.urlopen("http://localhost:8443/")
        logger.info(f"✅ Direct HTTP/1 GET test: status={response.status}")
        logger.info(f"📄 Response: {response.read().decode()[:100]}...")
        
        # Test POST request
        data = "Hello from HTTP/1 test!".encode('utf-8')
        req = urllib.request.Request("http://localhost:8443/api/echo", data=data)
        response = urllib.request.urlopen(req)
        logger.info(f"✅ Direct HTTP/1 POST test: status={response.status}")
        logger.info(f"📄 Echo response: {response.read().decode()}")
        
    except Exception as e:
        logger.error(f"❌ Direct HTTP/1 test failed: {e}")


def run_http3_client_demo():
    """Run the HTTP/3 client demo that communicates through the proxy."""
    logger.info("🔗 Connecting HTTP/3 client to proxy...")
    
    # Connect to the proxy (which should be listening on port 443 for HTTP/3)
    # The proxy will forward requests to the HTTP/1 server on port 8443
    client = connect_client("localhost", 443)
    
    try:
        # Test GET request through proxy
        logger.info("📤 Making HTTP/3 GET request to / through proxy")
        response = client.get("/")
        logger.info(f"✅ HTTP/3 GET response: status={response.status}")
        logger.info(f"📄 Response body: {response.text[:200]}...")
        
        # Test GET request to API endpoint
        logger.info("📤 Making HTTP/3 GET request to /api/status through proxy")
        response = client.get("/api/status")
        logger.info(f"✅ HTTP/3 GET /api/status response: status={response.status}")
        logger.info(f"📄 Response body: {response.text}")
        
        # Test POST request through proxy
        test_data = "Hello from HTTP/3 client through proxy!"
        logger.info(f"📤 Making HTTP/3 POST request to /api/echo with data: {test_data}")
        response = client.post("/api/echo", test_data)
        logger.info(f"✅ HTTP/3 POST response: status={response.status}")
        logger.info(f"📄 Echo response: {response.text}")
        
    except Exception as e:
        logger.error(f"❌ HTTP/3 client error: {e}")
    finally:
        client.close()
        logger.info("🔌 HTTP/3 client connection closed")


def main():
    """Main demo function."""
    print("=== HTTP/3 to HTTP/1 Demo ===")
    print("This demo shows an HTTP/3 client communicating with an HTTP/1 server through a proxy.")
    print("Make sure your HTTP/3 to HTTP/1 proxy is running on localhost:443")
    print("The proxy should forward requests to the HTTP/1 server on localhost:8443")
    print()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start HTTP/1 server in background thread
    server_thread = threading.Thread(target=run_http1_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    logger.info("⏳ Waiting for HTTP/1 server to start...")
    time.sleep(2)
    
    # Test the HTTP/1 server directly first
    test_http1_server_directly()
    
    print("\n" + "="*50)
    print("Now testing HTTP/3 client through proxy...")
    print("="*50)
    
    # Run HTTP/3 client demo
    run_http3_client_demo()
    
    print("\nDemo completed!")
    print("\nSummary:")
    print("- HTTP/1 server is running on localhost:8443")
    print("- HTTP/3 client connects to proxy on localhost:443")
    print("- Proxy forwards HTTP/3 requests to HTTP/1 server")
    print("- All communication is logged above")
    
    # Clean up
    stop_http1_server()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
        stop_http1_server()
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        stop_http1_server()
        raise 