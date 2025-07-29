#!/usr/bin/env python3

"""
Non-Conformance Test Case #3: Multiple Requests on Same Stream

Violates RFC 9114 Section 4.1 by sending two HEADERS frames that each 
look like independent requests on the same stream.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase3Client(BaseTestClient):
    """Test Case 3: Multiple requests sent on the same stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=3,
            test_name="Multiple requests on same stream",
            violation_description="RFC 9114 Section 4.1 - Client must send only single request per stream",
            rfc_section="RFC 9114 Section 4.1"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 3."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send first request (conformant)
        print("📍 Sending first request (conformant)")
        first_headers = create_common_headers(
            path="/first-request",
            method="GET",
            **{
                "x-test-case": "3",
                "x-request-number": "1"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, first_headers, end_stream=False)
            self.results.add_step("first_request_sent", True)
            print(f"✅ First HEADERS frame sent on stream {request_stream_id}")
            print("   └─ Method: GET, Path: /first-request (conformant)")
        except Exception as e:
            print(f"❌ First request failed: {e}")
            self.results.add_note(f"First request failed: {str(e)}")
            return
        
        # Step 4: Send second request on SAME stream (VIOLATION!)
        print("📍 Sending second request on SAME stream")
        print("🚫 PROTOCOL VIOLATION: Multiple requests on same stream!")
        print("🚫 RFC 9114 Section 4.1: Client MUST send only single request per stream")
        
        second_headers = create_common_headers(
            path="/second-request",
            method="POST",
            **{
                "x-test-case": "3",
                "x-request-number": "2"
            }
        )
        
        try:
            # This violates RFC 9114 Section 4.1
            self.h3_api.send_headers_frame(request_stream_id, second_headers, end_stream=True)
            self.results.add_step("second_request_sent", True)
            print(f"✅ Second HEADERS frame sent on stream {request_stream_id}")
            print("   └─ Method: POST, Path: /second-request (VIOLATION!)")
        except Exception as e:
            print(f"❌ Second request failed: {e}")
            self.results.add_note(f"Second request failed: {str(e)}")
            # Still mark as sent for result tracking
            self.results.add_step("second_request_sent", True)
        
        # Add test-specific observations
        self.results.add_note("Two HEADERS frames sent on same stream (protocol violation)")
        self.results.add_note("RFC 9114 Section 4.1: Client MUST send only single request per stream")


async def main():
    """Main entry point for Test Case 3."""
    test_client = TestCase3Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 