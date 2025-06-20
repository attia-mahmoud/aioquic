# Simple HTTP/3 API Documentation

A lightweight, easy-to-use HTTP/3 client and server API built on top of aioquic. This API provides a simple interface for making HTTP/3 requests without the complexity of managing QUIC connections manually.

## File Structure

The API is organized into three main files:

- **`simple_http3_client.py`** - Client implementation with `SimpleHttpClient` and `SimpleHttpClientWrapper` classes
- **`simple_http3_server.py`** - Server implementation with `SimpleHttpServer` class and ASGI application
- **`simple_http3_demo.py`** - Demo driver that shows how to use both client and server
- **`README_HTTP3_API.md`** - This documentation file

## Features

- ✅ **Simple API**: Easy-to-use synchronous interface
- ✅ **HTTP/3 Support**: Full HTTP/3 protocol implementation
- ✅ **TLS Encryption**: Secure connections with certificate validation
- ✅ **Automatic Connection Management**: No need to manually handle connection lifecycle
- ✅ **Request/Response Objects**: Clean response handling with status, headers, and body
- ✅ **Built-in Server**: Simple HTTP/3 server for testing and development
- ✅ **Modular Design**: Separate client and server implementations for easy integration
- ✅ **Comprehensive Header Logging**: Detailed logging of all HTTP headers for debugging and analysis

## Quick Start

### Option 1: Run the Complete Demo

```bash
python examples/simple_http3_demo.py
```

This will start a server and run various client tests automatically.

### Option 2: Use Client and Server Separately

#### Start the Server

```python
from simple_http3_server import start_server

# Start HTTP/3 server on localhost:8443
start_server("localhost", 8443)
```

#### Make Requests

```python
from simple_http3_client import connect_client

# Connect to the server
client = connect_client("localhost", 8443)

# Make a GET request
response = client.get("/")
print(f"Status: {response.status}")
print(f"Body: {response.text}")

# Make a POST request
response = client.post("/echo", "Hello HTTP/3!")
print(f"Response: {response.text}")

# Clean up
client.close()
```

## API Reference

### Client API (`simple_http3_client.py`)

#### `connect_client(host, port, ca_file)`

Connect to an HTTP/3 server and return a client object.

**Parameters:**
- `host` (str): Server hostname (default: "localhost")
- `port` (int): Server port (default: 4433)
- `ca_file` (str): Path to CA certificate file (default: "tests/pycacert.pem")

**Returns:**
- `SimpleHttpClientWrapper`: Client object with get() and post() methods

**Example:**
```python
from simple_http3_client import connect_client
client = connect_client("example.com", 443, "ca_cert.pem")
```

#### Client Methods

##### `client.get(path, headers=None)`

Make a GET request.

**Parameters:**
- `path` (str): Request path (e.g., "/api/users")
- `headers` (dict, optional): Additional HTTP headers

**Returns:**
- `HttpResponse`: Response object

**Example:**
```python
response = client.get("/api/users", {"Authorization": "Bearer token123"})
```

##### `client.post(path, data, headers=None)`

Make a POST request.

**Parameters:**
- `path` (str): Request path (e.g., "/api/users")
- `data` (str or bytes): Request body
- `headers` (dict, optional): Additional HTTP headers

**Returns:**
- `HttpResponse`: Response object

**Example:**
```python
response = client.post("/api/users", '{"name": "John"}', {"Content-Type": "application/json"})
```

##### `client.close()`

Close the client connection (no-op in current implementation).

### Server API (`simple_http3_server.py`)

#### `start_server(host, port, cert_file, key_file)`

Start an HTTP/3 server.

**Parameters:**
- `host` (str): Host to bind to (default: "localhost")
- `port` (int): Port to bind to (default: 4433)
- `cert_file` (str): Path to TLS certificate file (default: "tests/ssl_cert.pem")
- `key_file` (str): Path to TLS private key file (default: "tests/ssl_key.pem")

**Example:**
```python
from simple_http3_server import start_server
start_server("0.0.0.0", 8443, "my_cert.pem", "my_key.pem")
```

#### `SimpleHttpServer` Class

For more control over the server lifecycle:

```python
from simple_http3_server import SimpleHttpServer

# Create server instance
server = SimpleHttpServer("localhost", 8443)

# Start server (runs forever)
server.start()

# Or start asynchronously
import asyncio
asyncio.run(server.start_async())

# Stop server
server.stop()
```

### Response Object

The `HttpResponse` object provides easy access to response data:

**Properties:**
- `status` (int): HTTP status code (e.g., 200, 404, 500)
- `headers` (dict): Response headers
- `body` (bytes): Raw response body
- `text` (str): Response body as UTF-8 string

**Example:**
```python
response = client.get("/")
print(f"Status: {response.status}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Body: {response.text}")
```

## Complete Examples

### Basic Usage

```python
#!/usr/bin/env python3
import threading
import time
from simple_http3_server import start_server
from simple_http3_client import connect_client

def main():
    # Start server in background thread
    def run_server():
        start_server("localhost", 8443)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Connect and make requests
        client = connect_client("localhost", 8443)
        
        # GET request
        response = client.get("/")
        print(f"GET / -> Status: {response.status}")
        print(f"Response: {response.text}")
        
        # POST request
        response = client.post("/echo", "Hello HTTP/3 World!")
        print(f"POST /echo -> Status: {response.status}")
        print(f"Response: {response.text}")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

### Advanced Usage with Custom Headers

```python
from simple_http3_client import connect_client

client = connect_client("localhost", 8443)

# Custom headers
headers = {
    "Authorization": "Bearer your-token",
    "User-Agent": "MyApp/1.0",
    "Accept": "application/json"
}

response = client.get("/api/data", headers=headers)
print(f"Status: {response.status}")
print(f"Headers: {response.headers}")
```

### Binary Data Handling

```python
# Send binary data
binary_data = b"\x00\x01\x02\x03"
response = client.post("/echo", binary_data)

# Receive binary data
print(f"Received {len(response.body)} bytes")
```

## Server Endpoints

The built-in server provides these endpoints:

### GET `/`
Returns a simple HTML welcome page.

**Response:**
```html
<h1>Simple HTTP/3 Server</h1>
<p>Welcome to the simple HTTP/3 server!</p>
```

### POST `/echo`
Echoes back the request body.

**Request:**
```python
client.post("/echo", "Hello World")
```

**Response:**
```
Hello World
```

### Other Paths
Returns 404 "Not Found" for any other paths.

## Error Handling

The API handles common errors gracefully:

```python
try:
    client = connect_client("invalid-host", 8443)
    response = client.get("/")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Certificate Requirements

### Server Certificates
- **Certificate file**: PEM format TLS certificate
- **Private key file**: PEM format private key
- **Default**: Uses test certificates from `tests/ssl_cert.pem` and `tests/ssl_key.pem`

### Client Certificates
- **CA certificate**: PEM format CA certificate for server validation
- **Default**: Uses test CA certificate from `tests/pycacert.pem`

## Logging

The API uses Python's logging module with verbose output. To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Levels
- **INFO**: General operation information (default)
- **DEBUG**: Detailed connection and protocol information
- **WARNING**: Non-critical issues
- **ERROR**: Connection and protocol errors

### Header Logging

The API provides comprehensive header logging for both requests and responses:

#### Request Headers
When making requests, all headers are logged in detail:
```
📤 Sending GET request to /
📋 Request Headers:
  :method: GET
  :scheme: https
  :authority: localhost:8443
  :path: /
  user-agent: simple-http3/1.0
  x-custom-header: test-value
  accept: text/html,application/json
```

#### Response Headers
When receiving responses, all headers are logged:
```
📋 Parsing response headers: 4 header pairs
📋 Response Headers:
  :status: 200
  content-type: text/html; charset=utf-8
  server: SimpleHTTP3/1.0
  x-powered-by: aioquic
📊 Final status code: 200
```

#### Server-Side Header Logging
The server logs all incoming request headers:
```
📋 Incoming Request Headers:
  :method: POST
  :path: /echo
  :authority: localhost:8443
  content-type: application/json
  authorization: Bearer token123
  x-forwarded-for: 192.168.1.100
```

This detailed header logging is invaluable for:
- **Debugging**: See exactly what headers are being sent and received
- **Protocol Analysis**: Understand HTTP/3 header behavior
- **Security Auditing**: Monitor authentication and security headers
- **Performance Analysis**: Track header sizes and types

## Performance Notes

- Each request creates a new QUIC connection
- Connections are automatically closed after each request
- For high-performance applications, consider connection pooling
- The server can handle multiple concurrent connections

## Troubleshooting

### Common Issues

1. **Certificate Errors**
   ```
   Error: SSL certificate verification failed
   ```
   **Solution**: Ensure the CA certificate file is correct and the server certificate is valid.

2. **Connection Refused**
   ```
   Error: Connection refused
   ```
   **Solution**: Make sure the server is running and the host/port are correct.

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'aioquic'
   ```
   **Solution**: Install aioquic: `pip install aioquic`

4. **File Not Found**
   ```
   FileNotFoundError: [Errno 2] No such file or directory: 'tests/ssl_cert.pem'
   ```
   **Solution**: Ensure you're running from the correct directory or provide absolute paths to certificate files.

### Debug Mode

Enable debug logging to see detailed connection information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration Examples

### Using in Your Own Application

```python
# Import the modules you need
from simple_http3_client import connect_client, HttpResponse
from simple_http3_server import SimpleHttpServer

# Start your server
server = SimpleHttpServer("0.0.0.0", 8443)
# ... start server in background

# Use client in your application
client = connect_client("localhost", 8443)
response = client.get("/api/users")
# Process response...
client.close()
```

### Custom Server Endpoints

To add custom endpoints, modify the `simple_app` function in `simple_http3_server.py`:

```python
async def simple_app(scope, receive, send):
    if scope["type"] == "http":
        method = scope["method"]
        path = scope["path"]
        
        if method == "GET" and path == "/api/users":
            # Your custom endpoint
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json")],
            })
            await send({
                "type": "http.response.body",
                "body": b'[{"id": 1, "name": "John"}]',
            })
        # ... other endpoints
```

## Dependencies

- **aioquic**: QUIC protocol implementation
- **asyncio**: Python's async I/O framework
- **cryptography**: TLS/SSL support

## License

This API is part of the aioquic project and follows the same license terms. 