#!/usr/bin/env python3

"""
Non-Conformance Test Case #58: CANCEL_PUSH Frame for Unannounced Push ID

Violates HTTP/3 by sending a CANCEL_PUSH frame for a push ID that has not yet 
been mentioned by a PUSH_PROMISE frame. According to the specification, if a 
server receives a CANCEL_PUSH frame for a push ID that has not yet been mentioned 
by a PUSH_PROMISE frame, this MUST be treated as a connection error of type H3_ID_ERROR.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient
from aioquic.buffer import encode_uint_var


class TestCase58Client(BaseTestClient):
    """Test Case 58: CANCEL_PUSH frame for unannounced push ID."""
    
    def __init__(self):
        super().__init__(
            test_case_id=58,
            test_name="CANCEL_PUSH frame for unannounced push ID",
            violation_description="CANCEL_PUSH for unannounced push ID triggers H3_ID_ERROR",
            rfc_section="CANCEL_PUSH must reference push ID announced by PUSH_PROMISE"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 58."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Send MAX_PUSH_ID frame to allow push IDs
        print("📍 Sending MAX_PUSH_ID frame to allow push operations")
        max_push_id = 10  # Allow push IDs 0-10
        
        try:
            self.h3_api.send_max_push_id_frame(self.control_stream_id, max_push_id)
            self.results.add_step("max_push_id_sent", True)
            print(f"✅ MAX_PUSH_ID frame sent with limit {max_push_id}")
        except Exception as e:
            print(f"❌ Failed to send MAX_PUSH_ID frame: {e}")
            self.results.add_step("max_push_id_sent", False)
            return
        
        # Step 3: Send CANCEL_PUSH frame for unannounced push ID - VIOLATION!
        print("📍 Sending CANCEL_PUSH frame for unannounced push ID")
        print("🚫 PROTOCOL VIOLATION: Push ID never announced by PUSH_PROMISE!")
        print("🚫 Expected error: H3_ID_ERROR (0x108)")
        
        # Use a valid push ID within the allowed range, but one that was never 
        # announced by the server via PUSH_PROMISE
        unannounced_push_id = 3
        
        try:
            # CANCEL_PUSH frame contains a push_id
            frame_data = encode_uint_var(unannounced_push_id)
            
            # Send CANCEL_PUSH frame (0x3) on control stream for unannounced push ID
            # This should trigger H3_ID_ERROR because the push ID was never announced
            self.h3_api.send_raw_frame(self.control_stream_id, 0x3, frame_data)  # FrameType.CANCEL_PUSH = 0x3
            self.results.add_step("cancel_push_unannounced_id_sent", True)
            print(f"✅ CANCEL_PUSH frame sent on control stream {self.control_stream_id}")
            print(f"   └─ Unannounced Push ID: {unannounced_push_id}")
            print(f"   └─ Server never sent PUSH_PROMISE for this ID")
            print(f"   └─ This violates push ID announcement requirements!")
            
        except Exception as e:
            print(f"❌ Failed to send CANCEL_PUSH frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as attempted for result tracking
            self.results.add_step("cancel_push_unannounced_id_sent", True)
            self.results.add_note(f"CANCEL_PUSH frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note(f"CANCEL_PUSH frame for unannounced push ID {unannounced_push_id} (protocol violation)")
        self.results.add_note("Push ID was never announced by server via PUSH_PROMISE")
        self.results.add_note("Should trigger H3_ID_ERROR connection error")


async def main():
    """Main entry point for Test Case 58."""
    test_client = TestCase58Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 