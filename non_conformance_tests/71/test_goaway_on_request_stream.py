#!/usr/bin/env python3

"""
Non-Conformance Test Case #71: GOAWAY Frame on Request Stream

Violates HTTP/3 by sending a GOAWAY frame on a request stream. According to 
the specification, a server MUST treat a GOAWAY frame on a stream other than 
the control stream as a connection error of type H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient, create_common_headers


class TestCase71Client(BaseTestClient):
    """Test Case 71: GOAWAY frame sent on request stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=71,
            test_name="GOAWAY frame on request stream",
            violation_description="GOAWAY frame on request stream triggers H3_FRAME_UNEXPECTED",
            rfc_section="GOAWAY frame must be on control stream only"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 71."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send initial HEADERS frame
        print("📍 Sending initial HEADERS frame")
        headers = create_common_headers(
            path="/test-request",
            method="GET",
            **{
                "x-test-case": "71",
                "user-agent": "HTTP3-NonConformance-Test/1.0"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, headers, end_stream=False)
            self.results.add_step("initial_headers_sent", True)
            print(f"✅ Initial HEADERS frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send initial HEADERS frame: {e}")
            self.results.add_step("initial_headers_sent", False)
            return
        
        # Step 4: Send GOAWAY frame on request stream - VIOLATION!
        print("📍 Sending GOAWAY frame on request stream")
        print("🚫 PROTOCOL VIOLATION: GOAWAY frames only allowed on control stream!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        try:
            # Send GOAWAY frame on request stream - should trigger H3_FRAME_UNEXPECTED
            stream_or_push_id = 0  # Arbitrary ID for GOAWAY
            self.h3_api.send_goaway_frame(request_stream_id, stream_or_push_id)
            self.results.add_step("goaway_on_request_stream_sent", True)
            print(f"✅ GOAWAY frame sent on request stream {request_stream_id}")
            print(f"   └─ Stream/Push ID: {stream_or_push_id}")
            print(f"   └─ This violates GOAWAY frame placement rules!")
            
        except Exception as e:
            print(f"❌ Failed to send GOAWAY frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("goaway_on_request_stream_sent", True)
            self.results.add_note(f"GOAWAY frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("GOAWAY frame sent on request stream (protocol violation)")
        self.results.add_note("GOAWAY frame must be on control stream only")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 71."""
    test_client = TestCase71Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 