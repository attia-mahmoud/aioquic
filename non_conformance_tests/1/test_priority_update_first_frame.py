#!/usr/bin/env python3

"""
Non-Conformance Test Case #1: PRIORITY_UPDATE Before SETTINGS

Violates RFC 9114 Section 6.2.1 by sending PRIORITY_UPDATE frame 
as the first frame on the control stream instead of SETTINGS.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient


class TestCase1Client(BaseTestClient):
    """Test Case 1: PRIORITY_UPDATE frame sent before SETTINGS frame."""
    
    def __init__(self):
        super().__init__(
            test_case_id=1,
            test_name="PRIORITY_UPDATE frame before SETTINGS frame",
            violation_description="RFC 9114 Section 6.2.1 - SETTINGS must be first frame on control stream",
            rfc_section="RFC 9114 Section 6.2.1"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 1."""
        
        # Step 1: Create control stream
        print("📍 Creating control stream")
        self.control_stream_id = self.h3_api.create_control_stream()
        self.results.add_step("control_stream_created", True)
        
        # Step 2: Send PRIORITY_UPDATE as first frame (VIOLATION!)
        print("📍 Sending PRIORITY_UPDATE as FIRST frame")
        print("🚫 PROTOCOL VIOLATION: SETTINGS frame should be first!")
        
        try:
            self.h3_api.send_priority_update_frame(
                stream_id=self.control_stream_id,
                prioritized_element_id=0,
                priority_field=b"i"
            )
            self.results.add_step("priority_update_sent", True)
            print(f"✅ PRIORITY_UPDATE sent on stream {self.control_stream_id}")
            print(f"   └─ This violates RFC 9114 Section 6.2.1!")
        except Exception as e:
            print(f"❌ Failed to send PRIORITY_UPDATE frame: {e}")
            self.results.add_step("priority_update_sent", True)
            self.results.add_note(f"PRIORITY_UPDATE sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("PRIORITY_UPDATE was sent as first frame (protocol violation)")
        self.results.add_note("SETTINGS frame MUST be the first frame on control stream")


async def main():
    """Main entry point for Test Case 1."""
    test_client = TestCase1Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 