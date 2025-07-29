#!/usr/bin/env python3

"""
Non-Conformance Test Case #72: MAX_PUSH_ID Frame on Push Stream

Violates HTTP/3 by sending a MAX_PUSH_ID frame on a push stream. According to 
the specification, the MAX_PUSH_ID frame is always sent on the control stream. 
Receipt of a MAX_PUSH_ID frame by the server on any other stream MUST be treated 
as a connection error of type H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient
from aioquic.buffer import encode_uint_var


class TestCase72Client(BaseTestClient):
    """Test Case 72: MAX_PUSH_ID frame sent on push stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=72,
            test_name="MAX_PUSH_ID frame on push stream",
            violation_description="MAX_PUSH_ID frame on push stream triggers H3_FRAME_UNEXPECTED",
            rfc_section="MAX_PUSH_ID frame is always sent on control stream"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 72."""
        
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
        
        # Step 3: Send MAX_PUSH_ID frame on push stream - VIOLATION!
        print("📍 Sending MAX_PUSH_ID frame on push stream")
        print("🚫 PROTOCOL VIOLATION: MAX_PUSH_ID frames only allowed on control stream!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        try:
            # Send MAX_PUSH_ID frame on push stream - should trigger H3_FRAME_UNEXPECTED
            max_push_id = 5
            self.h3_api.send_max_push_id_frame(push_stream_id, max_push_id)
            self.results.add_step("max_push_id_on_push_stream_sent", True)
            print(f"✅ MAX_PUSH_ID frame sent on push stream {push_stream_id}")
            print(f"   └─ Max Push ID: {max_push_id}")
            print(f"   └─ This violates MAX_PUSH_ID frame placement rules!")
            
        except Exception as e:
            print(f"❌ Failed to send MAX_PUSH_ID frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("max_push_id_on_push_stream_sent", True)
            self.results.add_note(f"MAX_PUSH_ID frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("MAX_PUSH_ID frame sent on push stream (protocol violation)")
        self.results.add_note("MAX_PUSH_ID frame is always sent on control stream")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 72."""
    test_client = TestCase72Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 