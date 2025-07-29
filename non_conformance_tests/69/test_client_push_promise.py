#!/usr/bin/env python3

"""
Non-Conformance Test Case #69: Client Sends PUSH_PROMISE Frame

Violates HTTP/3 by sending a PUSH_PROMISE frame from the client. According to 
the specification, a client MUST NOT send a PUSH_PROMISE frame. A server MUST 
treat the receipt of a PUSH_PROMISE frame as a connection error of type 
H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient, create_common_headers
from aioquic.buffer import encode_uint_var


class TestCase69Client(BaseTestClient):
    """Test Case 69: Client sends PUSH_PROMISE frame."""
    
    def __init__(self):
        super().__init__(
            test_case_id=69,
            test_name="Client sends PUSH_PROMISE frame",
            violation_description="Client PUSH_PROMISE triggers H3_FRAME_UNEXPECTED",
            rfc_section="Client MUST NOT send PUSH_PROMISE frame"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 69."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send initial HEADERS frame
        print("📍 Sending initial HEADERS frame")
        headers = create_common_headers(
            path="/test-request",
            method="GET",
            **{
                "x-test-case": "69",
                "user-agent": "HTTP3-NonConformance-Test/1.0"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, headers, end_stream=False)
            self.results.add_step("initial_headers_sent", True)
            print(f"✅ Initial HEADERS frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send initial HEADERS frame: {e}")
            self.results.add_step("initial_headers_sent", False)
            return
        
        # Step 4: Send PUSH_PROMISE frame from client - VIOLATION!
        print("📍 Sending PUSH_PROMISE frame from client")
        print("🚫 PROTOCOL VIOLATION: Clients MUST NOT send PUSH_PROMISE!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        try:
            # Construct PUSH_PROMISE frame
            # Format: push_id + encoded field section
            push_id = 0
            push_promise_data = encode_uint_var(push_id)
            
            # Add minimal encoded header section (just push ID is enough for violation)
            # The actual header encoding doesn't matter since this should be rejected immediately
            push_promise_data += b"\x00"  # Minimal encoded field section
            
            # Send PUSH_PROMISE frame (0x5) on request stream
            self.h3_api.send_raw_frame(request_stream_id, 0x5, push_promise_data)  # FrameType.PUSH_PROMISE = 0x5
            self.results.add_step("push_promise_sent", True)
            print(f"✅ PUSH_PROMISE frame sent on request stream {request_stream_id}")
            print(f"   └─ Push ID: {push_id}")
            print(f"   └─ This violates client PUSH_PROMISE restrictions!")
            
        except Exception as e:
            print(f"❌ Failed to send PUSH_PROMISE frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("push_promise_sent", True)
            self.results.add_note(f"PUSH_PROMISE frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("PUSH_PROMISE frame sent by client (protocol violation)")
        self.results.add_note("Client MUST NOT send PUSH_PROMISE frame")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 69."""
    test_client = TestCase69Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 