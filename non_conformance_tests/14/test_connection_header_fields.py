#!/usr/bin/env python3

"""
Non-Conformance Test Case #14: Connection-Specific Header Fields

Violates HTTP/3 specifications by sending a request containing 
connection-specific header fields. The client MUST NOT generate 
an HTTP/3 field section containing connection-specific fields.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase14Client(BaseTestClient):
    """Test Case 14: Request with connection-specific header fields."""
    
    def __init__(self):
        super().__init__(
            test_case_id=14,
            test_name="Connection-specific header fields",
            violation_description="Connection-specific fields MUST NOT be used in HTTP/3",
            rfc_section="HTTP/3 Header Field Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 14."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with connection-specific headers - VIOLATION!
        print("📍 Sending HEADERS frame with connection-specific header fields")
        print("🚫 PROTOCOL VIOLATION: Connection-specific fields MUST NOT be used in HTTP/3!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with forbidden connection-specific fields
        # These headers are specific to HTTP/1.1 connection management and forbidden in HTTP/3
        violation_headers = [
            (b":method", b"GET"),
            (b":path", b"/test-connection-headers"),
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"connection", b"keep-alive"),  # FORBIDDEN - connection management
            (b"upgrade", b"websocket"),  # FORBIDDEN - protocol upgrade
            (b"proxy-connection", b"keep-alive"),  # FORBIDDEN - proxy connection management
            (b"keep-alive", b"timeout=5, max=1000"),  # FORBIDDEN - connection keep-alive
            (b"te", b"trailers"),  # FORBIDDEN - transfer encoding (except trailers is special case)
            (b"x-test-case", b"14"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("connection_headers_sent", True)
            print(f"✅ HEADERS frame with connection-specific fields sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ Forbidden headers: Connection, Upgrade, Proxy-Connection, Keep-Alive, TE")
            print(f"   └─ This violates HTTP/3 connection-specific field restrictions!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("connection_headers_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Attempt to send DATA frame (if headers were accepted)
        print("📍 Sending DATA frame with request body")
        request_body = b'{"message": "This request contains forbidden connection-specific headers"}'
        
        try:
            self.h3_api.send_data_frame(request_stream_id, request_body, end_stream=True)
            self.results.add_step("request_body_sent", True)
            print(f"✅ DATA frame sent on stream {request_stream_id}")
            print(f"   └─ Payload: {len(request_body)} bytes")
        except Exception as e:
            print(f"❌ Failed to send DATA frame: {e}")
            self.results.add_step("request_body_sent", False)
            self.results.add_note(f"DATA frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Request sent with connection-specific header fields (protocol violation)")
        self.results.add_note("HTTP/3 field section MUST NOT contain connection-specific fields")
        self.results.add_note("Forbidden headers: Connection, Upgrade, Proxy-Connection, Keep-Alive, TE")


async def main():
    """Main entry point for Test Case 14."""
    test_client = TestCase14Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 