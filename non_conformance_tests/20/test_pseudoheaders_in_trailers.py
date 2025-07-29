#!/usr/bin/env python3

"""
Non-Conformance Test Case #20: Pseudo-Headers in Trailing HEADERS

Violates HTTP/3 specifications by sending pseudo-header fields in 
a trailing HEADERS frame. Pseudo-header fields MUST NOT appear 
in trailer sections sent by the client.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase20Client(BaseTestClient):
    """Test Case 20: Pseudo-headers in trailing HEADERS frame."""
    
    def __init__(self):
        super().__init__(
            test_case_id=20,
            test_name="Pseudo-headers in trailing HEADERS frame",
            violation_description="Pseudo-headers MUST NOT appear in trailer sections",
            rfc_section="HTTP/3 Trailer Field Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 20."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send initial HEADERS frame (conformant)
        print("📍 Sending initial HEADERS frame")
        initial_headers = create_common_headers(
            path="/test-pseudo-trailers",
            method="POST",
            **{
                "x-test-case": "20",
                "content-type": "application/json",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "te": "trailers",  # Indicate we'll send trailers
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, initial_headers, end_stream=False)
            self.results.add_step("initial_headers_sent", True)
            print(f"✅ Initial HEADERS frame sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(initial_headers)} header fields")
        except Exception as e:
            print(f"❌ Failed to send initial HEADERS frame: {e}")
            self.results.add_step("initial_headers_sent", False)
            return
        
        # Step 4: Send DATA frame with request body
        print("📍 Sending DATA frame with request body")
        request_body = b'{"message": "This request will have invalid pseudo-headers in trailers"}'
        
        try:
            self.h3_api.send_data_frame(request_stream_id, request_body, end_stream=False)
            self.results.add_step("request_body_sent", True)
            print(f"✅ DATA frame sent on stream {request_stream_id}")
            print(f"   └─ Payload: {len(request_body)} bytes")
        except Exception as e:
            print(f"❌ Failed to send DATA frame: {e}")
            self.results.add_step("request_body_sent", False)
            self.results.add_note(f"DATA frame sending failed: {str(e)}")
            return
        
        # Step 5: Send trailing HEADERS frame with pseudo-headers - VIOLATION!
        print("📍 Sending trailing HEADERS frame with pseudo-headers")
        print("🚫 PROTOCOL VIOLATION: Pseudo-headers MUST NOT appear in trailer sections!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create trailing headers with forbidden pseudo-header fields
        # Trailers should only contain regular header fields, never pseudo-headers
        violation_trailers = [
            # FORBIDDEN pseudo-headers in trailers
            (b":path", b"/updated-path"),  # FORBIDDEN - pseudo-header in trailer
            (b":method", b"PUT"),  # FORBIDDEN - pseudo-header in trailer
            (b":status", b"200"),  # FORBIDDEN - pseudo-header in trailer
            (b":scheme", b"http"),  # FORBIDDEN - pseudo-header in trailer
            # Valid trailer fields (these would be OK in isolation)
            (b"x-request-id", b"12345"),
            (b"x-processing-time", b"150ms"),
            (b"x-trailer-test", b"pseudo-headers-violation"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_trailers, end_stream=True)
            self.results.add_step("pseudo_trailers_sent", True)
            print(f"✅ Trailing HEADERS frame with pseudo-headers sent on stream {request_stream_id}")
            print(f"   └─ Trailers: {len(violation_trailers)} header fields")
            print(f"   └─ Forbidden pseudo-headers: :path, :method, :status, :scheme")
            print(f"   └─ This violates HTTP/3 trailer field restrictions!")
        except Exception as e:
            print(f"❌ Failed to send trailing HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("pseudo_trailers_sent", True)
            self.results.add_note(f"Trailing HEADERS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Trailing HEADERS frame sent with pseudo-headers (protocol violation)")
        self.results.add_note("Pseudo-headers MUST NOT appear in trailer sections")
        self.results.add_note("Forbidden pseudo-headers in trailers: :path, :method, :status, :scheme")
        self.results.add_note("Valid trailers should only contain regular header fields")


async def main():
    """Main entry point for Test Case 20."""
    test_client = TestCase20Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 