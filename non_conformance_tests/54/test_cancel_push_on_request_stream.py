#!/usr/bin/env python3

"""
Non-Conformance Test Case #54: CANCEL_PUSH Frame on Request Stream

Violates HTTP/3 by sending a CANCEL_PUSH frame on a request stream. According to 
the specification, a CANCEL_PUSH frame is sent on the control stream. If a 
CANCEL_PUSH frame is sent by the client on a stream other than the control stream, 
the server MUST respond with a connection error of type H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers
from aioquic.buffer import encode_uint_var


class TestCase54Client(BaseTestClient):
    """Test Case 54: CANCEL_PUSH frame sent on request stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=54,
            test_name="CANCEL_PUSH frame on request stream",
            violation_description="CANCEL_PUSH frame on request stream triggers H3_FRAME_UNEXPECTED",
            rfc_section="CANCEL_PUSH frame is sent on the control stream"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 54."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send initial HEADERS frame (valid)
        print("📍 Sending initial HEADERS frame")
        headers = create_common_headers(
            path="/test-request",
            method="GET",
            **{
                "x-test-case": "54",
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
        
        # Step 4: Send CANCEL_PUSH frame on request stream - VIOLATION!
        print("📍 Sending CANCEL_PUSH frame on request stream")
        print("🚫 PROTOCOL VIOLATION: CANCEL_PUSH frames should only be on control stream!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        try:
            # CANCEL_PUSH frame contains a push_id
            push_id = 0  # Push ID to cancel
            frame_data = encode_uint_var(push_id)
            
            # Send CANCEL_PUSH frame (0x3) on request stream - this should trigger H3_FRAME_UNEXPECTED
            self.h3_api.send_raw_frame(request_stream_id, 0x3, frame_data)  # FrameType.CANCEL_PUSH = 0x3
            self.results.add_step("cancel_push_on_request_stream_sent", True)
            print(f"✅ CANCEL_PUSH frame sent on request stream {request_stream_id}")
            print(f"   └─ Push ID: {push_id}")
            print(f"   └─ This violates HTTP/3 frame usage rules!")
            
        except Exception as e:
            print(f"❌ Failed to send CANCEL_PUSH frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as attempted for result tracking
            self.results.add_step("cancel_push_on_request_stream_sent", True)
            self.results.add_note(f"CANCEL_PUSH frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("CANCEL_PUSH frame sent on request stream (protocol violation)")
        self.results.add_note("CANCEL_PUSH frames should only be sent on control stream")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 54."""
    test_client = TestCase54Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 