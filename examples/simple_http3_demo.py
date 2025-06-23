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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_http3_demo")


def run_server_demo():
    """Run the server in a background thread."""
    logger.info("Starting server...")
    start_server("localhost", 8443)


def run_client_demo():
    """Run the client demo with a simple request."""
    logger.info("Connecting to server...")
    client = connect_client("localhost", 443)
    
    try:
        # Make a simple GET request
        logger.info("Making GET request to /")
        response = client.get("/")
        logger.info(f"Response status: {response.status}")
        logger.info(f"Response body: {response.text}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.close()
        logger.info("Client connection closed")


def main():
    """Main demo function."""
    print("=== Simple HTTP/3 Demo ===")
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server_demo, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Run client demo
    run_client_demo()
    
    print("Demo completed!")


if __name__ == "__main__":
    main() 