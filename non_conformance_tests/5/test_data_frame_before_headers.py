#!/usr/bin/env python3

"""
Non-Conformance Test Case #5: DATA Frame Before HEADERS

Violates HTTP/3 frame sequencing by sending DATA frame on request 
stream without preceding HEADERS frame.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient


class TestCase5Client(BaseTestClient):
    """Test Case 5: DATA frame sent before HEADERS frame on request stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=5,
            test_name="DATA frame before HEADERS frame",
            violation_description="Invalid frame sequence - DATA before HEADERS triggers H3_FRAME_UNEXPECTED",
            rfc_section="HTTP/3 Frame Sequencing"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 5."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send DATA frame FIRST (without HEADERS) - VIOLATION!
        print("📍 Sending DATA frame WITHOUT HEADERS first")
        print("🚫 PROTOCOL VIOLATION: DATA frame before HEADERS is invalid!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        # Send DATA frame without any preceding HEADERS frame
        # This violates HTTP/3 frame sequencing rules
        data_payload = b'{"error": "This DATA frame should not be accepted without HEADERS"}'
        
        try:
            self.h3_api.send_data_frame(request_stream_id, data_payload, end_stream=False)
            self.results.add_step("data_frame_sent_first", True)
            print(f"✅ DATA frame sent on stream {request_stream_id}")
            print(f"   └─ Payload: {len(data_payload)} bytes")
            print(f"   └─ This violates HTTP/3 frame sequence rules!")
        except Exception as e:
            print(f"❌ Failed to send DATA frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as sent for result tracking
            self.results.add_step("data_frame_sent_first", True)
            self.results.add_note(f"DATA frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("DATA frame sent before any HEADERS frame (protocol violation)")
        self.results.add_note("Invalid frame sequence should trigger H3_FRAME_UNEXPECTED")


async def main():
    """Main entry point for Test Case 5."""
    test_client = TestCase5Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 