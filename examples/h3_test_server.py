#!/usr/bin/env python3

"""
Simple HTTP/3 Test Server for Non-Conformance Testing

This server logs all incoming frames and can be used to test how 
non-conformant HTTP/3 behavior is handled.
"""

import asyncio
import logging
import ssl
from typing import Dict, Optional

from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import DataReceived, H3Event, HeadersReceived
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent
from aioquic.tls import SessionTicket

# Enable debug logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("h3_test_server")


class H3TestServerProtocol(QuicConnectionProtocol):
    """
    Test server protocol that logs all HTTP/3 events.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http: Optional[H3Connection] = None
        self._request_handlers: Dict[int, asyncio.Task] = {}
        logger.info("🟢 New client connection established")
    
    def quic_event_received(self, event: QuicEvent) -> None:
        """Handle QUIC events and route to HTTP layer."""
        logger.debug(f"📡 QUIC event: {type(event).__name__}")
        
        # Initialize HTTP connection if not done yet
        if self._http is None:
            self._http = H3Connection(self._quic)
            logger.info("🔗 HTTP/3 connection initialized")
        
        # Process HTTP events
        try:
            for http_event in self._http.handle_event(event):
                self.http_event_received(http_event)
        except Exception as e:
            logger.error(f"❌ Error processing HTTP event: {e}")
            # Log the specific exception for non-conformance analysis
            logger.error(f"🔍 Exception type: {type(e).__name__}")
            logger.error(f"🔍 Exception details: {str(e)}")
    
    def http_event_received(self, event: H3Event) -> None:
        """Handle HTTP/3 events."""
        logger.info(f"📥 HTTP/3 event: {type(event).__name__}")
        
        if isinstance(event, HeadersReceived):
            logger.info(f"📋 Headers received on stream {event.stream_id}:")
            for name, value in event.headers:
                logger.info(f"   {name.decode()}: {value.decode()}")
            
            # Create task to handle the request
            task = asyncio.create_task(
                self._handle_request(event.stream_id, event.headers)
            )
            self._request_handlers[event.stream_id] = task
            
        elif isinstance(event, DataReceived):
            logger.info(f"📦 Data received on stream {event.stream_id}: {len(event.data)} bytes")
            if event.stream_ended:
                logger.info(f"🔚 Stream {event.stream_id} ended")
    
    async def _handle_request(self, stream_id: int, headers) -> None:
        """Handle an HTTP request."""
        try:
            # Extract method and path
            method = None
            path = None
            for name, value in headers:
                if name == b":method":
                    method = value.decode()
                elif name == b":path":
                    path = value.decode()
            
            logger.info(f"🚀 Handling {method} {path} on stream {stream_id}")
            
            # Send a simple response
            response_headers = [
                (b":status", b"200"),
                (b"content-type", b"text/plain; charset=utf-8"),
                (b"server", b"aioquic-test-server"),
            ]
            
            self._http.send_headers(stream_id, response_headers)
            
            response_body = (
                f"Hello from HTTP/3 test server!\n"
                f"You requested: {method} {path}\n"
                f"Stream ID: {stream_id}\n"
                f"This server logs all non-conformant behavior.\n"
            ).encode()
            
            self._http.send_data(stream_id, response_body, end_stream=True)
            logger.info(f"✅ Response sent for stream {stream_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling request on stream {stream_id}: {e}")
        finally:
            # Clean up the task
            if stream_id in self._request_handlers:
                del self._request_handlers[stream_id]


def create_certificate_files():
    """Create temporary SSL certificate files for testing."""
    import tempfile
    import os
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import datetime
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Create temporary files
    cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
    key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
    
    # Write certificate and key
    cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
    cert_file.close()
    
    key_file.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))
    key_file.close()
    
    return cert_file.name, key_file.name


async def main():
    """Run the HTTP/3 test server."""
    host = "localhost"
    port = 4433
    
    logger.info("🚀 Starting HTTP/3 Test Server")
    logger.info("=====================================")
    logger.info(f"📡 Listening on: {host}:{port}")
    logger.info("🔍 This server logs all non-conformant HTTP/3 behavior")
    logger.info("⚠️  Using self-signed certificate for testing")
    
    # Create temporary certificate files
    cert_file, key_file = create_certificate_files()
    
    try:
        # Create QUIC configuration
        configuration = QuicConfiguration(
            alpn_protocols=H3_ALPN,
            is_client=False,
            max_datagram_frame_size=65536,
        )
        
        # Load certificate and private key
        configuration.load_cert_chain(cert_file, key_file)
        
        # Start server
        server = await serve(
            host=host,
            port=port,
            configuration=configuration,
            create_protocol=H3TestServerProtocol,
        )
        
        logger.info("✅ Server started successfully!")
        logger.info("💡 Run the non-conformance test client to test protocol violations")
        logger.info("🛑 Press Ctrl+C to stop the server")
        
        try:
            # Keep server running forever
            await asyncio.Future()
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        finally:
            server.close()
            
    finally:
        # Clean up temporary certificate files
        import os
        try:
            os.unlink(cert_file)
            os.unlink(key_file)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n�� Server stopped") 