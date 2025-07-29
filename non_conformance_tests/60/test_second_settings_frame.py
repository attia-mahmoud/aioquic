#!/usr/bin/env python3

"""
Non-Conformance Test Case #60: Second SETTINGS Frame

Violates HTTP/3 by sending a second SETTINGS frame on the control stream. 
According to the specification, if a server receives a second SETTINGS frame 
on the control stream, the server MUST respond with a connection error of 
type H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient


class TestCase60Client(BaseTestClient):
    """Test Case 60: Second SETTINGS frame sent on control stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=60,
            test_name="Second SETTINGS frame",
            violation_description="Second SETTINGS frame triggers H3_FRAME_UNEXPECTED",
            rfc_section="Only one SETTINGS frame allowed per control stream"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 60."""
        
        # Step 1: Set up conformant HTTP/3 connection (includes first SETTINGS frame)
        await self.setup_conformant_connection()
        
        # Step 2: Send second SETTINGS frame on control stream - VIOLATION!
        print("📍 Sending second SETTINGS frame on control stream")
        print("🚫 PROTOCOL VIOLATION: Only one SETTINGS frame allowed!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        try:
            # Send a second SETTINGS frame on the same control stream
            # This should trigger H3_FRAME_UNEXPECTED because only one SETTINGS frame is allowed
            self.h3_api.send_settings_frame(self.control_stream_id)
            self.results.add_step("second_settings_frame_sent", True)
            print(f"✅ Second SETTINGS frame sent on control stream {self.control_stream_id}")
            print(f"   └─ This violates the one SETTINGS frame per control stream rule!")
            
        except Exception as e:
            print(f"❌ Failed to send second SETTINGS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as attempted for result tracking
            self.results.add_step("second_settings_frame_sent", True)
            self.results.add_note(f"Second SETTINGS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Second SETTINGS frame sent on control stream (protocol violation)")
        self.results.add_note("Only one SETTINGS frame is allowed per control stream")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 60."""
    test_client = TestCase60Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 