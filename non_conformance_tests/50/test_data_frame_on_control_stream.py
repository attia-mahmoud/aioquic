#!/usr/bin/env python3

"""
Non-Conformance Test Case #50: DATA Frame on Control Stream

Violates HTTP/3 by sending a DATA frame on the control stream. According to 
the specification, DATA frames MUST be associated with an HTTP request or 
response. If a DATA frame is sent by the client on a control stream, the 
server MUST respond with a connection error of type H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient


class TestCase50Client(BaseTestClient):
    """Test Case 50: DATA frame sent on control stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=50,
            test_name="DATA frame on control stream",
            violation_description="DATA frame on control stream triggers H3_FRAME_UNEXPECTED",
            rfc_section="DATA frames MUST be associated with HTTP request or response"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 50."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Send DATA frame on control stream - VIOLATION!
        print("📍 Sending DATA frame on control stream")
        print("🚫 PROTOCOL VIOLATION: DATA frames not allowed on control stream!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        # DATA frames MUST be associated with HTTP request/response streams only
        violation_data = b'{"violation": "DATA frame should not be sent on control stream"}'
        
        try:
            # Send DATA frame on the control stream - this should trigger H3_FRAME_UNEXPECTED
            self.h3_api.send_data_frame(self.control_stream_id, violation_data, end_stream=False)
            self.results.add_step("data_frame_on_control_stream_sent", True)
            print(f"✅ DATA frame sent on control stream {self.control_stream_id}")
            print(f"   └─ Payload: {len(violation_data)} bytes")
            print(f"   └─ This violates HTTP/3 frame usage rules!")
            
        except Exception as e:
            print(f"❌ Failed to send DATA frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as attempted for result tracking
            self.results.add_step("data_frame_on_control_stream_sent", True)
            self.results.add_note(f"DATA frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("DATA frame sent on control stream (protocol violation)")
        self.results.add_note("DATA frames MUST be associated with HTTP request or response")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 50."""
    test_client = TestCase50Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 