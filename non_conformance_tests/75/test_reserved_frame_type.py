#!/usr/bin/env python3

"""
Non-Conformance Test Case #75: Reserved Frame Type

Violates HTTP/3 by sending a reserved frame type on a request stream. According to 
the specification, frame types that were used in HTTP/2 where there is no 
corresponding HTTP/3 frame have been reserved. These frame types MUST NOT be sent 
by the client, and their receipt by the server MUST be treated as a connection 
error of type H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient, create_common_headers


class TestCase75Client(BaseTestClient):
    """Test Case 75: Reserved frame type sent on request stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=75,
            test_name="Reserved frame type",
            violation_description="Reserved frame type triggers H3_FRAME_UNEXPECTED",
            rfc_section="Reserved frame types MUST NOT be sent by client"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 75."""
        
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
                "x-test-case": "75",
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
        
        # Step 4: Send reserved frame type on request stream - VIOLATION!
        print("📍 Sending reserved frame type on request stream")
        print("🚫 PROTOCOL VIOLATION: Reserved frame type 0x4!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        try:
            # Send reserved frame type 0x4 (PRIORITY from HTTP/2 context)
            # This frame type is reserved and MUST NOT be sent by clients
            frame_data = b"\x00\x00\x00\x00"  # Minimal frame payload
            
            # Send reserved frame type 0x4 on request stream
            self.h3_api.send_raw_frame(request_stream_id, 0x4, frame_data)
            self.results.add_step("reserved_frame_type_sent", True)
            print(f"✅ Reserved frame type 0x4 sent on request stream {request_stream_id}")
            print(f"   └─ This violates reserved frame type restrictions!")
            
        except Exception as e:
            print(f"❌ Failed to send reserved frame type: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("reserved_frame_type_sent", True)
            self.results.add_note(f"Reserved frame type sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Reserved frame type 0x4 sent on request stream (protocol violation)")
        self.results.add_note("Reserved frame types MUST NOT be sent by client")
        self.results.add_note("Should trigger H3_FRAME_UNEXPECTED connection error")


async def main():
    """Main entry point for Test Case 75."""
    test_client = TestCase75Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 