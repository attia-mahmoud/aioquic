#!/usr/bin/env python3

"""
Non-Conformance Test Case #19: Response Pseudo-Headers in Client Request

Violates HTTP/3 specifications by sending a request containing 
response pseudo-header fields. Pseudo-header fields defined for 
responses MUST NOT appear in requests.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase19Client(BaseTestClient):
    """Test Case 19: Request with response pseudo-header fields."""
    
    def __init__(self):
        super().__init__(
            test_case_id=19,
            test_name="Response pseudo-headers in client request",
            violation_description="Response pseudo-headers MUST NOT appear in requests",
            rfc_section="HTTP/3 Request Pseudo-Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 19."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with response pseudo-headers - VIOLATION!
        print("📍 Sending HEADERS frame with response pseudo-header fields")
        print("🚫 PROTOCOL VIOLATION: Response pseudo-headers MUST NOT appear in requests!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with forbidden response pseudo-header fields
        # :status is defined for responses only and MUST NOT appear in requests
        violation_headers = [
            # Valid request pseudo-headers
            (b":method", b"GET"),
            (b":path", b"/test-response-pseudo-headers"),
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            # FORBIDDEN response pseudo-header in request
            (b":status", b"200"),  # FORBIDDEN - :status is for responses only
            # Regular headers
            (b"x-test-case", b"19"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("response_pseudo_headers_sent", True)
            print(f"✅ HEADERS frame with response pseudo-headers sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ Forbidden response pseudo-header: :status")
            print(f"   └─ This violates HTTP/3 request pseudo-header restrictions!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("response_pseudo_headers_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Attempt to send DATA frame (if headers were accepted)
        print("📍 Sending DATA frame with request body")
        request_body = b'{"message": "This request contains forbidden response pseudo-header :status"}'
        
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
        self.results.add_note("Request sent with response pseudo-header :status (protocol violation)")
        self.results.add_note("Response pseudo-headers MUST NOT appear in requests")
        self.results.add_note("Valid request pseudo-headers: :method, :path, :scheme, :authority only")


async def main():
    """Main entry point for Test Case 19."""
    test_client = TestCase19Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 