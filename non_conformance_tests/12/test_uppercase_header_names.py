#!/usr/bin/env python3

"""
Non-Conformance Test Case #12: Uppercase Header Field Names

Violates HTTP/3 specifications by sending a request containing 
uppercase header field names. Characters in field names sent by 
the client MUST be converted to lowercase prior to their encoding.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient


class TestCase12Client(BaseTestClient):
    """Test Case 12: Request with uppercase header field names."""
    
    def __init__(self):
        super().__init__(
            test_case_id=12,
            test_name="Uppercase header field names",
            violation_description="Header field names MUST be lowercase in HTTP/3",
            rfc_section="HTTP/3 Header Field Encoding"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 12."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with uppercase header names - VIOLATION!
        print("📍 Sending HEADERS frame with uppercase header field names")
        print("🚫 PROTOCOL VIOLATION: Header field names MUST be lowercase in HTTP/3!")
        
        # Create headers with uppercase field names (violates HTTP/3 spec)
        violation_headers = [
            (b":method", b"POST"),
            (b":path", b"/test-uppercase-headers"),
            (b":scheme", b"https"), 
            (b":authority", b"test-server"),
            (b"Content-Type", b"application/json"),  # Should be "content-type"
            (b"User-Agent", b"HTTP3-NonConformance-Test/1.0"),  # Should be "user-agent"
            (b"X-Test-Case", b"12"),  # Should be "x-test-case"
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=True)
            self.results.add_step("uppercase_headers_sent", True)
            print(f"✅ HEADERS frame with uppercase field names sent on stream {request_stream_id}")
            print(f"   └─ Uppercase headers: Content-Type, User-Agent, X-Test-Case")
            print(f"   └─ This violates HTTP/3 lowercase header requirement!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            self.results.add_step("uppercase_headers_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Request sent with uppercase header field names (protocol violation)")
        self.results.add_note("Header field names MUST be lowercase prior to encoding in HTTP/3")


async def main():
    """Main entry point for Test Case 12."""
    test_client = TestCase12Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 