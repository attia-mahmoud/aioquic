#!/usr/bin/env python3
"""
Simple HTTP/3 Server Implementation

A lightweight HTTP/3 server built on top of aioquic.
"""

import asyncio
import logging
from typing import Dict, Optional

from aioquic.asyncio import serve
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import DataReceived, H3Event, HeadersReceived
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent
from aioquic.tls import SessionTicket

# Import the existing server components
from http3_server import HttpServerProtocol, SessionTicketStore

logger = logging.getLogger("simple_http3_server")

# Global server instance
_server = None


# Simple ASGI application for testing
async def simple_app(scope, receive, send):
    """Simple ASGI application that handles basic HTTP requests."""
    logger.info(f"🔵 ASGI app received request: {scope['method']} {scope['path']}")
    
    if scope["type"] == "http":
        method = scope["method"]
        path = scope["path"]
        
        if method == "GET" and path == "/":
            logger.info("📄 Serving homepage")
            # Return a simple homepage
            response_headers = [
                (b"content-type", b"text/html; charset=utf-8"),
                (b"server", b"SimpleHTTP3/1.0"),
                (b"x-powered-by", b"aioquic"),
            ]
            
            logger.info("📋 Response Headers:")
            for key, value in response_headers:
                logger.info(f"  {key.decode()}: {value.decode()}")
            
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": response_headers,
            })
            await send({
                "type": "http.response.body",
                "body": b"<h1>Simple HTTP/3 Server</h1><p>Welcome to the simple HTTP/3 server!</p>",
            })
            logger.info("✅ Homepage served successfully")
        
        elif method == "POST" and path == "/echo":
            logger.info("🔄 Processing echo request")
            # Echo the request body
            body = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if message.get("more_body", False):
                        continue
                    break
            
            logger.info(f"📤 Echoing back {len(body)} bytes")
            response_headers = [
                (b"content-type", b"text/plain; charset=utf-8"),
                (b"server", b"SimpleHTTP3/1.0"),
                (b"x-powered-by", b"aioquic"),
                (b"content-length", str(len(body)).encode()),
            ]
            
            logger.info("📋 Response Headers:")
            for key, value in response_headers:
                logger.info(f"  {key.decode()}: {value.decode()}")
            
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": response_headers,
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
            logger.info("✅ Echo response sent successfully")
        
        else:
            logger.warning(f"❌ 404 Not Found: {method} {path}")
            # 404 for unknown paths
            response_headers = [
                (b"content-type", b"text/plain; charset=utf-8"),
                (b"server", b"SimpleHTTP3/1.0"),
                (b"x-powered-by", b"aioquic"),
            ]
            
            logger.info("📋 Response Headers:")
            for key, value in response_headers:
                logger.info(f"  {key.decode()}: {value.decode()}")
            
            await send({
                "type": "http.response.start",
                "status": 404,
                "headers": response_headers,
            })
            await send({
                "type": "http.response.body",
                "body": b"Not Found",
            })


# Create a custom server protocol that uses our simple app
class SimpleHttpServerProtocol(HttpServerProtocol):
    """Custom server protocol that uses our simple ASGI application."""
    
    def http_event_received(self, event: H3Event) -> None:
        """Override to use our simple application."""
        if isinstance(event, HeadersReceived) and event.stream_id not in self._handlers:
            logger.info(f"🌐 New HTTP/3 request received on stream {event.stream_id}")
            
            # Parse headers
            headers = {}
            method = b""
            path = b""
            authority = b""
            
            # Log all incoming request headers in detail
            logger.info("📋 Incoming Request Headers:")
            for key, value in event.headers:
                if key == b":method":
                    method = value
                    logger.info(f"  {key.decode()}: {value.decode()}")
                elif key == b":path":
                    path = value
                    logger.info(f"  {key.decode()}: {value.decode()}")
                elif key == b":authority":
                    authority = value
                    logger.info(f"  {key.decode()}: {value.decode()}")
                elif key.startswith(b":"):
                    # Log other pseudo-headers
                    logger.info(f"  {key.decode()}: {value.decode()}")
                else:
                    headers[key.decode()] = value.decode()
                    logger.info(f"  {key.decode()}: {value.decode()}")
            
            logger.info(f"📋 Request Summary: {method.decode()} {path.decode()}")
            logger.debug(f"📋 Regular headers: {headers}")
            
            # Create scope
            scope = {
                "client": None,
                "extensions": {},
                "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
                "http_version": "3",
                "method": method.decode(),
                "path": path.decode(),
                "query_string": b"",
                "raw_path": path,
                "root_path": "",
                "scheme": "https",
                "type": "http",
            }
            
            # Create handler
            from http3_server import HttpRequestHandler
            handler = HttpRequestHandler(
                authority=authority,
                connection=self._http,
                protocol=self,
                scope=scope,
                stream_ended=event.stream_ended,
                stream_id=event.stream_id,
                transmit=self.transmit,
            )
            self._handlers[event.stream_id] = handler
            logger.debug(f"🔧 Created handler for stream {event.stream_id}")
            asyncio.ensure_future(handler.run_asgi(simple_app))
        elif (
            isinstance(event, (DataReceived, HeadersReceived))
            and event.stream_id in self._handlers
        ):
            logger.debug(f"📦 Forwarding event to handler for stream {event.stream_id}")
            handler = self._handlers[event.stream_id]
            handler.http_event_received(event)


class SimpleHttpServer:
    """Simple HTTP/3 server class."""
    
    def __init__(self, host: str = "localhost", port: int = 4433, cert_file: str = "tests/ssl_cert.pem", key_file: str = "tests/ssl_key.pem"):
        """
        Initialize the HTTP/3 server.
        
        Args:
            host: Host to bind to (default: localhost)
            port: Port to bind to (default: 4433)
            cert_file: Path to TLS certificate file
            key_file: Path to TLS private key file
        """
        self.host = host
        self.port = port
        self.cert_file = cert_file
        self.key_file = key_file
        self._server = None
        logger.info(f"🔧 SimpleHttpServer initialized for {host}:{port}")
    
    async def start_async(self):
        """Start the server asynchronously."""
        global _server
        
        logger.info(f"🚀 Starting HTTP/3 server on {self.host}:{self.port}")
        logger.info(f"🔐 Using certificate: {self.cert_file}")
        logger.info(f"🔑 Using private key: {self.key_file}")
        
        # Create configuration
        configuration = QuicConfiguration(
            alpn_protocols=H3_ALPN,
            is_client=False,
            max_datagram_frame_size=65536,
        )
        configuration.load_cert_chain(self.cert_file, self.key_file)
        logger.debug("🔧 QUIC configuration created")
        
        # Start server
        self._server = await serve(
            host=self.host,
            port=self.port,
            configuration=configuration,
            create_protocol=SimpleHttpServerProtocol,
            session_ticket_fetcher=SessionTicketStore().pop,
            session_ticket_handler=SessionTicketStore().add,
            retry=False,
        )
        _server = self._server
        
        logger.info(f"✅ HTTP/3 server started successfully on {self.host}:{self.port}")
        logger.info("🔄 Server is ready to accept connections")
        
        # Keep server running
        await asyncio.Future()  # Run forever
    
    def start(self):
        """Start the server (synchronous interface)."""
        logger.info(f"🎯 Starting HTTP/3 server process")
        try:
            asyncio.run(self.start_async())
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
    
    def stop(self):
        """Stop the server."""
        if self._server:
            self._server.close()
            logger.info("🛑 Server stopped")


async def _start_server_async(host: str, port: int, cert_file: str, key_file: str):
    """Async function to start the HTTP/3 server."""
    server = SimpleHttpServer(host, port, cert_file, key_file)
    await server.start_async()


def start_server(host: str = "localhost", port: int = 4433, cert_file: str = "tests/ssl_cert.pem", key_file: str = "tests/ssl_key.pem"):
    """
    Start an HTTP/3 server.
    
    Args:
        host: Host to bind to (default: localhost)
        port: Port to bind to (default: 4433)
        cert_file: Path to TLS certificate file
        key_file: Path to TLS private key file
    
    Returns:
        None (runs forever)
    """
    server = SimpleHttpServer(host, port, cert_file, key_file)
    server.start() 