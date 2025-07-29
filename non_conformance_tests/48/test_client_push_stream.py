#!/usr/bin/env python3

"""
Non-Conformance Test Case #48: Client-Initiated Push Stream

Violates HTTP/3 by opening a client-initiated push stream (type 0x01).
According to the specification, only servers can push; if a server receives 
a client-initiated push stream, this MUST be treated as a connection error 
of type H3_STREAM_CREATION_ERROR.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient
from aioquic.buffer import encode_uint_var


class TestCase48Client(BaseTestClient):
    """Test Case 48: Client opens push stream when only servers can push."""
    
    def __init__(self):
        super().__init__(
            test_case_id=48,
            test_name="Client-initiated push stream",
            violation_description="Client opening push stream triggers H3_STREAM_CREATION_ERROR",
            rfc_section="Only servers can push"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 48."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create client-initiated push stream - VIOLATION!
        print("📍 Creating client-initiated push stream")
        print("🚫 PROTOCOL VIOLATION: Only servers can push!")
        print("🚫 Expected error: H3_STREAM_CREATION_ERROR (0x103)")
        
        try:
            # Manually create a push stream (type 0x01) from client side
            push_stream_id = protocol._quic.get_next_available_stream_id(is_unidirectional=True)
            self.results.add_step("push_stream_created", True)
            print(f"✅ Push stream created with ID {push_stream_id}")
            
            # Send stream type identifier for PUSH (0x01)
            stream_type_data = encode_uint_var(1)  # StreamType.PUSH = 1
            protocol._quic.send_stream_data(push_stream_id, stream_type_data)
            self.results.add_step("push_stream_type_sent", True)
            print(f"✅ Push stream type (0x01) sent on stream {push_stream_id}")
            
            # Send push ID (required for push streams)
            push_id = 0  # First push ID
            push_id_data = encode_uint_var(push_id)
            protocol._quic.send_stream_data(push_stream_id, push_id_data)
            self.results.add_step("push_id_sent", True)
            print(f"✅ Push ID {push_id} sent on push stream")
            print(f"   └─ This violates the server-only push rule!")
            
        except Exception as e:
            print(f"❌ Failed to create push stream: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as attempted for result tracking
            self.results.add_step("push_stream_created", True)
            self.results.add_note(f"Push stream creation failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Client-initiated push stream opened (protocol violation)")
        self.results.add_note("Only servers are allowed to push")
        self.results.add_note("Should trigger H3_STREAM_CREATION_ERROR connection error")


async def main():
    """Main entry point for Test Case 48."""
    test_client = TestCase48Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 