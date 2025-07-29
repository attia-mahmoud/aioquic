#!/usr/bin/env python3

"""
Non-Conformance Test Case #39: Push Stream without MAX_PUSH_ID

Tests server behavior when it attempts to initiate push streams without 
the client having sent a MAX_PUSH_ID frame. According to HTTP/3 
specifications, a client MUST treat receipt of a push stream as a 
connection error of type H3_ID_ERROR when no MAX_PUSH_ID frame has been sent.
This test deliberately omits sending MAX_PUSH_ID and observes server behavior.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase39Client(BaseTestClient):
    """Test Case 39: Server push without client sending MAX_PUSH_ID frame."""
    
    def __init__(self):
        super().__init__(
            test_case_id=39,
            test_name="Push stream without MAX_PUSH_ID frame",
            violation_description="Server MUST NOT push when client hasn't sent MAX_PUSH_ID",
            rfc_section="HTTP/3 Server Push Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 39."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Deliberately NOT send MAX_PUSH_ID frame
        print("📍 Deliberately NOT sending MAX_PUSH_ID frame")
        print("🚫 CLIENT BEHAVIOR: No MAX_PUSH_ID sent - server push should be disabled")
        print("🚫 Expected: Server MUST NOT initiate any push streams")
        
        # Note: We explicitly do NOT call any method to send MAX_PUSH_ID
        self.results.add_step("max_push_id_deliberately_omitted", True)
        print("✅ MAX_PUSH_ID frame deliberately omitted")
        print("   └─ Any server push attempt would violate HTTP/3 specification")
        
        # Step 3: Send a simple request that might trigger server push
        print("📍 Sending request that typically triggers server push")
        request_stream_id = self.create_request_stream(protocol)
        
        headers = create_common_headers(
            path="/index.html",
            method="GET",
            **{
                "x-test-case": "39",
                "user-agent": "HTTP3-NonConformance-Test/1.0"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, headers, end_stream=True)
            self.results.add_step("request_sent", True)
            print(f"✅ Request sent on stream {request_stream_id}")
            print(f"   └─ Server MUST NOT push since no MAX_PUSH_ID was sent")
        except Exception as e:
            print(f"❌ Failed to send request: {e}")
            self.results.add_step("request_sent", False)
            self.results.add_note(f"Request sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Client deliberately did NOT send MAX_PUSH_ID frame")
        self.results.add_note("Server MUST NOT initiate push streams without MAX_PUSH_ID")
        self.results.add_note("Any push stream attempts would violate HTTP/3 specification")


async def main():
    """Main entry point for Test Case 39."""
    test_client = TestCase39Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 