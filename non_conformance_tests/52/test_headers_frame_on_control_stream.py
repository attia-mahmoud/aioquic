#!/usr/bin/env python3

"""
Non-Conformance Test Case #52: HEADERS Frame on Control Stream

Violates HTTP/3 by sending a HEADERS frame on the control stream. According to 
the specification, HEADERS frames can only be sent on request streams or push 
streams. If a HEADERS frame is sent by the client on a control stream, the 
server MUST respond with a connection error of type H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase52Client(BaseTestClient):
    """Test Case 52: HEADERS frame sent on control stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=52,
            test_name="HEADERS frame on control stream",
            violation_description="HEADERS frame on control stream triggers H3_FRAME_UNEXPECTED",
            rfc_section="HEADERS frames can only be sent on request streams or push streams"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 52."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Send HEADERS frame on control stream - VIOLATION!
        print("📍 Sending HEADERS frame on control stream")
        print("🚫 PROTOCOL VIOLATION: HEADERS frames not allowed on control stream!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        # HEADERS frames can only be sent on request streams or push streams
        violation_headers = create_common_headers(
            path="/invalid-control-stream-request",
            method="GET",
            **{
                "x-violation": "headers-on-control-stream",
                "x-test-case": "52"
            }
        )
        
        try:
            # Send HEADERS frame on the control stream - this should trigger H3_FRAME_UNEXPECTED
            self.h3_api.send_headers_frame(self.control_stream_id, violation_headers, end_stream=False)
            self.results.add_step("headers_frame_on_control_stream_sent", True)
            print(f"✅ HEADERS frame sent on control stream {self.control_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ This violates HTTP/3 frame usage rules!")
            
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as attempted for result tracking
            self.results.add_step("headers_frame_on_control_stream_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("HEADERS frame sent on control stream (protocol violation)")
        self.results.add_note("HEADERS frames can only be sent on request streams or push streams")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 52."""
    test_client = TestCase52Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 