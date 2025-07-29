#!/usr/bin/env python3

"""
Non-Conformance Test Case #10: Transfer-Encoding Header in HTTP/3

Violates HTTP/3 specifications by sending a request containing a 
Transfer-Encoding: chunked header. Transfer codings are not defined 
for HTTP/3 and the Transfer-Encoding header field MUST NOT be used.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase10Client(BaseTestClient):
    """Test Case 10: Request with Transfer-Encoding header."""
    
    def __init__(self):
        super().__init__(
            test_case_id=10,
            test_name="Transfer-Encoding header in HTTP/3 request",
            violation_description="Transfer-Encoding header MUST NOT be used in HTTP/3",
            rfc_section="HTTP/3 Header Field Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 10."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with forbidden Transfer-Encoding header - VIOLATION!
        print("📍 Sending HEADERS frame with Transfer-Encoding: chunked")
        print("🚫 PROTOCOL VIOLATION: Transfer-Encoding header MUST NOT be used in HTTP/3!")
        
        # Create headers with forbidden Transfer-Encoding header
        violation_headers = create_common_headers(
            path="/test-transfer-encoding",
            method="POST",
            **{
                "x-test-case": "10",
                "transfer-encoding": "chunked",  # FORBIDDEN in HTTP/3
                "user-agent": "HTTP3-NonConformance-Test/1.0"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=True)
            self.results.add_step("transfer_encoding_headers_sent", True)
            print(f"✅ HEADERS frame with Transfer-Encoding sent on stream {request_stream_id}")
            print(f"   └─ This violates HTTP/3 transfer coding restrictions!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            self.results.add_step("transfer_encoding_headers_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Request sent with Transfer-Encoding: chunked header (protocol violation)")
        self.results.add_note("Transfer-Encoding header field MUST NOT be used in HTTP/3")


async def main():
    """Main entry point for Test Case 10."""
    test_client = TestCase10Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 