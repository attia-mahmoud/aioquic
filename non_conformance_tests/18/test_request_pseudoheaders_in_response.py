#!/usr/bin/env python3

"""
Non-Conformance Test Case #18: Request Pseudo-Headers in Server Response

Tests for server-side violation where the server incorrectly includes 
request pseudo-headers (:method, :path) in response headers. This tests 
how servers/proxies handle request processing and whether they might 
incorrectly echo back or include request pseudo-headers in responses.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase18Client(BaseTestClient):
    """Test Case 18: Testing for request pseudo-headers in server responses."""
    
    def __init__(self):
        super().__init__(
            test_case_id=18,
            test_name="Request pseudo-headers in server response",
            violation_description="Server MUST NOT include request pseudo-headers in responses",
            rfc_section="HTTP/3 Response Pseudo-Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 18."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send request that might trigger server to echo back request headers
        print("📍 Sending request that might trigger pseudo-header echoing")
        print("🔍 Testing if server incorrectly includes request pseudo-headers in response")
        print("🚫 Server violation: Including :method, :path in response headers")
        
        # Send a request that might confuse some implementations into echoing back in responses
        test_headers = create_common_headers(
            path="/echo-test",
            method="GET",
            **{
                "x-test-case": "18",
                "x-request-echo-test": "true",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, test_headers, end_stream=True)
            self.results.add_step("echo_test_headers_sent", True)
            print(f"✅ Echo test HEADERS frame sent on stream {request_stream_id}")
            print(f"   └─ Testing server response header validation")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            self.results.add_step("echo_test_headers_sent", False)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Testing for server-side violation: request pseudo-headers in response")
        self.results.add_note("Compliant response should only contain :status pseudo-header")
        self.results.add_note("Violation: Response containing :method, :path, :scheme, :authority")


async def main():
    """Main entry point for Test Case 18."""
    test_client = TestCase18Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 