#!/usr/bin/env python3
"""
Simple HTTP/3 Client Implementation

A lightweight HTTP/3 client built on top of aioquic.
"""

import asyncio
import logging
from typing import Dict, Optional, Union

from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import DataReceived, H3Event, HeadersReceived
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent
from aioquic.tls import SessionTicket

logger = logging.getLogger("simple_http3_client")


class SimpleHttpClient(QuicConnectionProtocol):
    """Simple HTTP/3 client that provides easy-to-use methods."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = H3Connection(self._quic)
        self._request_events = {}
        self._request_waiter = {}
        logger.debug("🔧 SimpleHttpClient initialized")
        
    def quic_event_received(self, event: QuicEvent) -> None:
        """Handle QUIC events and route to HTTP layer."""
        logger.debug(f"📡 QUIC event received: {type(event).__name__}")
        if self._http is not None:
            for http_event in self._http.handle_event(event):
                self.http_event_received(http_event)
    
    def http_event_received(self, event: H3Event) -> None:
        """Handle HTTP/3 events and complete requests."""
        logger.debug(f"🌐 HTTP/3 event received: {type(event).__name__} for stream {event.stream_id}")
        if isinstance(event, (HeadersReceived, DataReceived)):
            stream_id = event.stream_id
            if stream_id in self._request_events:
                self._request_events[stream_id].append(event)
                if event.stream_ended:
                    logger.info(f"✅ Stream {stream_id} completed, resolving request")
                    waiter = self._request_waiter.pop(stream_id)
                    waiter.set_result(self._request_events.pop(stream_id))
    
    async def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> 'HttpResponse':
        """Make a GET request."""
        logger.info(f"📤 Making GET request to {path}")
        return await self._request("GET", path, headers=headers)
    
    async def post(self, path: str, data: Union[str, bytes], headers: Optional[Dict[str, str]] = None) -> 'HttpResponse':
        """Make a POST request."""
        logger.info(f"📤 Making POST request to {path} with {len(data) if isinstance(data, bytes) else len(data.encode())} bytes")
        if isinstance(data, str):
            data = data.encode('utf-8')
        return await self._request("POST", path, data=data, headers=headers)
    
    async def _request(self, method: str, path: str, data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None) -> 'HttpResponse':
        """Make an HTTP request."""
        if headers is None:
            headers = {}
        
        logger.debug(f"🔧 Creating {method} request to {path}")
        
        # Create request headers
        request_headers = [
            (b":method", method.encode()),
            (b":scheme", b"https"),
            (b":authority", self._quic.configuration.server_name.encode()),
            (b":path", path.encode()),
            (b"user-agent", b"simple-http3/1.0"),
        ]
        
        # Add custom headers
        for key, value in headers.items():
            request_headers.append((key.encode(), value.encode()))
        
        # Log all request headers in detail
        logger.info(f"📤 Sending {method} request to {path}")
        logger.info("📋 Request Headers:")
        for key, value in request_headers:
            if key.startswith(b":"):
                logger.info(f"  {key.decode()}: {value.decode()}")
            else:
                logger.info(f"  {key.decode()}: {value.decode()}")
        
        # Create stream and send headers
        stream_id = self._quic.get_next_available_stream_id()
        logger.debug(f"🆔 Using stream ID: {stream_id}")
        
        self._http.send_headers(
            stream_id=stream_id,
            headers=request_headers,
            end_stream=not data
        )
        
        # Send data if provided
        if data:
            logger.debug(f"📦 Sending {len(data)} bytes of data")
            self._http.send_data(stream_id=stream_id, data=data, end_stream=True)
        
        # Wait for response
        waiter = self._loop.create_future()
        self._request_events[stream_id] = []
        self._request_waiter[stream_id] = waiter
        logger.debug(f"⏳ Waiting for response on stream {stream_id}")
        self.transmit()
        
        events = await asyncio.shield(waiter)
        logger.info(f"✅ Received response for {method} {path}")
        return HttpResponse(events)


class HttpResponse:
    """Simple HTTP response object."""
    
    def __init__(self, events):
        self.events = events
        self.status = 200
        self.headers = {}
        self.body = b""
        self._parse_events()
        logger.debug(f"📄 Parsed response: status={self.status}, body_length={len(self.body)}")
    
    def _parse_events(self):
        """Parse HTTP/3 events into response data."""
        for event in self.events:
            if isinstance(event, HeadersReceived):
                logger.info(f"📋 Parsing response headers: {len(event.headers)} header pairs")
                logger.info("📋 Response Headers:")
                for key, value in event.headers:
                    if key == b":status":
                        self.status = int(value.decode())
                        logger.info(f"  {key.decode()}: {self.status}")
                    elif not key.startswith(b":"):
                        self.headers[key.decode()] = value.decode()
                        logger.info(f"  {key.decode()}: {value.decode()}")
                    else:
                        # Log pseudo-headers (like :status) but don't store them
                        logger.info(f"  {key.decode()}: {value.decode()}")
                logger.info(f"📊 Final status code: {self.status}")
            elif isinstance(event, DataReceived):
                logger.debug(f"📦 Received {len(event.data)} bytes of data")
                self.body += event.data
    
    @property
    def text(self) -> str:
        """Get response body as text."""
        return self.body.decode('utf-8')
    
    def __str__(self) -> str:
        return f"HttpResponse(status={self.status}, body={self.body[:100]}...)"


def save_session_ticket(ticket: SessionTicket) -> None:
    """Callback for session ticket handling."""
    logger.debug(f"🎫 New session ticket received: {len(ticket.ticket)} bytes")


async def _make_request_async(host: str, port: int, ca_file: str, method: str, path: str, data: Optional[Union[str, bytes]] = None, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
    """Async function to make a single HTTP/3 request."""
    logger.info(f"🔗 Connecting to HTTP/3 server at {host}:{port}")
    logger.info(f"🔐 Using CA certificate: {ca_file}")
    
    # Create configuration
    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=H3_ALPN,
    )
    configuration.load_verify_locations(ca_file)
    configuration.server_name = host
    logger.debug("🔧 Client QUIC configuration created")
    
    # Connect and make request
    async with connect(
        host=host,
        port=port,
        configuration=configuration,
        create_protocol=SimpleHttpClient,
        session_ticket_handler=save_session_ticket,
    ) as client:
        logger.info(f"✅ Connected to HTTP/3 server at {host}:{port}")
        
        if method.upper() == "GET":
            return await client.get(path, headers)
        elif method.upper() == "POST":
            return await client.post(path, data, headers)
        else:
            raise ValueError(f"Unsupported method: {method}")


class SimpleHttpClientWrapper:
    """Wrapper for the async client to provide sync-like interface."""
    
    def __init__(self, host: str, port: int, ca_file: str):
        self.host = host
        self.port = port
        self.ca_file = ca_file
        logger.debug(f"🔧 Client wrapper created for {host}:{port}")
    
    def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        """Make a GET request (synchronous interface)."""
        logger.info(f"📤 Making GET request to {self.host}:{self.port}{path}")
        return asyncio.run(_make_request_async(self.host, self.port, self.ca_file, "GET", path, headers))
    
    def post(self, path: str, data: Union[str, bytes], headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        """Make a POST request (synchronous interface)."""
        data_size = len(data) if isinstance(data, bytes) else len(data.encode())
        logger.info(f"📤 Making POST request to {self.host}:{self.port}{path} with {data_size} bytes")
        return asyncio.run(_make_request_async(self.host, self.port, self.ca_file, "POST", path, data, headers))
    
    def close(self):
        """Close the connection (no-op for this implementation)."""
        logger.debug("🔧 Client wrapper close called (no-op)")


def connect_client(host: str = "localhost", port: int = 4433, ca_file: str = "tests/pycacert.pem") -> SimpleHttpClientWrapper:
    """
    Connect to an HTTP/3 server.
    
    Args:
        host: Server hostname (default: localhost)
        port: Server port (default: 4433)
        ca_file: Path to CA certificate file
    
    Returns:
        SimpleHttpClientWrapper: Client object with get() and post() methods
    """
    logger.info(f"🔗 Creating client connection to {host}:{port}")
    return SimpleHttpClientWrapper(host, port, ca_file) 