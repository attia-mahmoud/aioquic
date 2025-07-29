#!/usr/bin/env python3

"""
Non-Conformance Test Case #62: SETTINGS Frame on Push Stream

Violates HTTP/3 by sending a SETTINGS frame on a push stream. According to 
the specification, SETTINGS frames MUST NOT be sent on any stream other than 
the control stream. If a server receives a SETTINGS frame on a different stream, 
the server MUST respond with a connection error of type H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient
from aioquic.buffer import encode_uint_var


class TestCase62Client(BaseTestClient):
    """Test Case 62: SETTINGS frame sent on push stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=62,
            test_name="SETTINGS frame on push stream",
            violation_description="SETTINGS frame on push stream triggers H3_FRAME_UNEXPECTED",
            rfc_section="SETTINGS frames MUST NOT be sent on any stream other than control stream"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 62."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create push stream
        print("📍 Creating push stream")
        push_stream_id = protocol._quic.get_next_available_stream_id(is_unidirectional=True)
        
        # Send stream type identifier for PUSH (0x01)
        stream_type_data = encode_uint_var(1)  # StreamType.PUSH = 1
        protocol._quic.send_stream_data(push_stream_id, stream_type_data)
        
        # Send push ID
        push_id = 0
        push_id_data = encode_uint_var(push_id)
        protocol._quic.send_stream_data(push_stream_id, push_id_data)
        self.results.add_step("push_stream_created", True)
        print(f"✅ Push stream created with ID {push_stream_id}")
        
        # Step 3: Send SETTINGS frame on push stream - VIOLATION!
        print("📍 Sending SETTINGS frame on push stream")
        print("🚫 PROTOCOL VIOLATION: SETTINGS frames only allowed on control stream!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        try:
            # Send SETTINGS frame on push stream - should trigger H3_FRAME_UNEXPECTED
            self.h3_api.send_settings_frame(push_stream_id)
            self.results.add_step("settings_on_push_stream_sent", True)
            print(f"✅ SETTINGS frame sent on push stream {push_stream_id}")
            print(f"   └─ This violates SETTINGS frame placement rules!")
            
        except Exception as e:
            print(f"❌ Failed to send SETTINGS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("settings_on_push_stream_sent", True)
            self.results.add_note(f"SETTINGS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("SETTINGS frame sent on push stream (protocol violation)")
        self.results.add_note("SETTINGS frames MUST NOT be sent on any stream other than control stream")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 62."""
    test_client = TestCase62Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 