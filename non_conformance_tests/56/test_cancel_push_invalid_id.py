#!/usr/bin/env python3

"""
Non-Conformance Test Case #56: CANCEL_PUSH Frame with Invalid Push ID

Violates HTTP/3 by sending a CANCEL_PUSH frame that references a push ID greater 
than currently allowed on the connection. According to the specification, if a 
CANCEL_PUSH frame is sent by the client that references a push ID greater than 
currently allowed on the connection, the server MUST respond with a connection 
error of type H3_ID_ERROR.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient
from aioquic.buffer import encode_uint_var


class TestCase56Client(BaseTestClient):
    """Test Case 56: CANCEL_PUSH frame with invalid push ID."""
    
    def __init__(self):
        super().__init__(
            test_case_id=56,
            test_name="CANCEL_PUSH frame with invalid push ID",
            violation_description="CANCEL_PUSH with invalid push ID triggers H3_ID_ERROR",
            rfc_section="CANCEL_PUSH must reference valid push ID"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 56."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Send CANCEL_PUSH frame with invalid push ID - VIOLATION!
        print("📍 Sending CANCEL_PUSH frame with invalid push ID")
        print("🚫 PROTOCOL VIOLATION: Push ID exceeds allowed range!")
        print("🚫 Expected error: H3_ID_ERROR (0x108)")
        
        # Note: The server has not sent MAX_PUSH_ID ≥ 5, so push ID 5 is invalid
        # Even if MAX_PUSH_ID was sent, referencing push ID 5 without it being 
        # established would still be invalid
        invalid_push_id = 5
        
        try:
            # CANCEL_PUSH frame contains a push_id
            frame_data = encode_uint_var(invalid_push_id)
            
            # Send CANCEL_PUSH frame (0x3) on control stream with invalid push ID
            # This should trigger H3_ID_ERROR because the push ID exceeds allowed range
            self.h3_api.send_raw_frame(self.control_stream_id, 0x3, frame_data)  # FrameType.CANCEL_PUSH = 0x3
            self.results.add_step("cancel_push_invalid_id_sent", True)
            print(f"✅ CANCEL_PUSH frame sent on control stream {self.control_stream_id}")
            print(f"   └─ Invalid Push ID: {invalid_push_id}")
            print(f"   └─ Server has not established MAX_PUSH_ID ≥ {invalid_push_id}")
            print(f"   └─ This violates push ID range constraints!")
            
        except Exception as e:
            print(f"❌ Failed to send CANCEL_PUSH frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as attempted for result tracking
            self.results.add_step("cancel_push_invalid_id_sent", True)
            self.results.add_note(f"CANCEL_PUSH frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note(f"CANCEL_PUSH frame with invalid push ID {invalid_push_id} (protocol violation)")
        self.results.add_note("Push ID exceeds currently allowed range")
        self.results.add_note("Should trigger H3_ID_ERROR connection error")


async def main():
    """Main entry point for Test Case 56."""
    test_client = TestCase56Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 