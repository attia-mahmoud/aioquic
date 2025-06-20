#!/usr/bin/env python3
"""
Simple HTTP/3 Demo Driver

This file demonstrates how to use the Simple HTTP/3 API by importing
the client and server implementations and running a complete demo.
"""

import logging
import threading
import time

# Import our client and server implementations
from simple_http3_client import connect_client
from simple_http3_server import start_server

# Set up verbose logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_http3_demo")


def run_server_demo():
    """Run the server in a background thread."""
    logger.info("🔄 Starting server in background thread")
    start_server("localhost", 8443)


def run_client_demo():
    """Run the client demo with various requests."""
    logger.info("🔗 Connecting to server...")
    client = connect_client("localhost", 8443)
    
    try:
        # Test GET request
        logger.info("📤 Making GET request...")
        response = client.get("/")
        logger.info(f"✅ GET / -> Status: {response.status}")
        logger.info(f"📄 Body: {response.text[:200]}...")
        
        # Test POST request
        logger.info("📤 Making POST request...")
        response = client.post("/echo", "Hello from Simple HTTP/3!")
        logger.info(f"✅ POST /echo -> Status: {response.status}")
        logger.info(f"📄 Body: {response.text}")
        
        # Test 404
        logger.info("📤 Testing 404...")
        response = client.get("/nonexistent")
        logger.info(f"✅ GET /nonexistent -> Status: {response.status}")
        logger.info(f"📄 Body: {response.text}")
        
        # Test with custom headers
        logger.info("📤 Testing with custom headers...")
        headers = {
            "X-Custom-Header": "test-value", 
            "User-Agent": "SimpleHTTP3Demo/1.0",
            "Accept": "text/html,application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "X-Request-ID": "demo-12345"
        }
        response = client.get("/", headers=headers)
        logger.info(f"✅ GET / with headers -> Status: {response.status}")
        
        # Test binary data
        logger.info("📤 Testing binary data...")
        binary_data = b"\x00\x01\x02\x03\x04\x05"
        response = client.post("/echo", binary_data)
        logger.info(f"✅ POST /echo with binary data -> Status: {response.status}")
        logger.info(f"📄 Echoed back {len(response.body)} bytes")
        
        # Test with more complex headers
        logger.info("📤 Testing with complex headers...")
        complex_headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "Content-Type": "application/json",
            "X-Forwarded-For": "192.168.1.100",
            "X-Real-IP": "192.168.1.100",
            "X-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        response = client.post("/echo", '{"message": "test"}', complex_headers)
        logger.info(f"✅ POST /echo with complex headers -> Status: {response.status}")
        
    except Exception as e:
        logger.error(f"❌ Error during client demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        client.close()
        logger.info("🔧 Client connection closed")


def main():
    """Main demo function."""
    print("=== Simple HTTP/3 API Demo ===")
    print("🚀 Starting demo with verbose logging...")
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server_demo, daemon=True)
    server_thread.start()
    logger.info("✅ Server thread started")
    
    # Wait for server to start
    logger.info("⏳ Waiting 2 seconds for server to start...")
    time.sleep(2)
    
    # Run client demo
    run_client_demo()
    
    logger.info("🎉 Demo completed successfully!")


if __name__ == "__main__":
    main() 