#!/usr/bin/env python3

"""
Non-Conformance Test Case #22: Incorrect Header Ordering

Violates HTTP/3 specifications by sending headers where regular header 
fields appear before pseudo-header fields. All pseudo-header fields 
MUST appear in the header section before regular header fields in requests.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase22Client(BaseTestClient):
    """Test Case 22: Incorrect header ordering (regular headers before pseudo-headers)."""
    
    def __init__(self):
        super().__init__(
            test_case_id=22,
            test_name="Incorrect header ordering",
            violation_description="Pseudo-headers MUST appear before regular headers in requests",
            rfc_section="HTTP/3 Header Field Ordering Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 22."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with incorrect ordering - VIOLATION!
        print("📍 Sending HEADERS frame with incorrect header ordering")
        print("🚫 PROTOCOL VIOLATION: Regular headers appear before pseudo-headers!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with INCORRECT ordering - regular headers before pseudo-headers
        # This violates HTTP/3 specification which requires pseudo-headers to come first
        violation_headers = [
            # WRONG: Regular headers first (should come after pseudo-headers)
            (b"host", b"test-server"),  # Regular header
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),  # Regular header
            (b"accept", b"application/json"),  # Regular header
            (b"x-test-case", b"22"),  # Regular header
            (b"content-type", b"application/json"),  # Regular header
            
            # WRONG: Pseudo-headers after regular headers (should come first)
            (b":method", b"POST"),  # Pseudo-header
            (b":path", b"/test-header-ordering"),  # Pseudo-header
            (b":scheme", b"https"),  # Pseudo-header
            (b":authority", b"test-server"),  # Pseudo-header
            
            # More regular headers
            (b"authorization", b"Bearer test-token"),
            (b"cache-control", b"no-cache"),
        ]
        
        try:
            # Use send_raw_headers_frame to bypass any automatic header reordering
            self.h3_api.send_raw_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("incorrect_header_ordering_sent", True)
            print(f"✅ HEADERS frame with incorrect ordering sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ Order: Regular headers first, then pseudo-headers")
            print(f"   └─ This violates HTTP/3 header ordering requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("incorrect_header_ordering_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Attempt to send DATA frame (if headers were accepted)
        print("📍 Sending DATA frame with request body")
        request_body = b'{"message": "This request has incorrect header ordering"}'
        
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
        self.results.add_note("HEADERS frame sent with incorrect ordering (protocol violation)")
        self.results.add_note("Regular headers appeared before pseudo-headers")
        self.results.add_note("Pseudo-headers MUST appear before regular headers in requests")
        self.results.add_note("Correct order: :method, :path, :scheme, :authority, then regular headers")


async def main():
    """Main entry point for Test Case 22."""
    test_client = TestCase22Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 