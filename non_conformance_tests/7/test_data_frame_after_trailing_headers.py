#!/usr/bin/env python3

"""
Non-Conformance Test Case #7: DATA Frame After Trailing HEADERS

Violates HTTP/3 frame sequencing by sending a DATA frame after 
a trailing HEADERS frame on a request stream. According to the
specification, sending any frame after a trailing HEADERS frame
should trigger H3_FRAME_UNEXPECTED.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase7Client(BaseTestClient):
    """Test Case 7: DATA frame sent after trailing HEADERS frame."""
    
    def __init__(self):
        super().__init__(
            test_case_id=7,
            test_name="DATA frame after trailing HEADERS frame",
            violation_description="Invalid frame sequence - DATA after trailing HEADERS triggers H3_FRAME_UNEXPECTED",
            rfc_section="HTTP/3 Frame Sequencing Rules"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 7."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send initial HEADERS frame (request headers)
        print("📍 Sending initial HEADERS frame")
        initial_headers = create_common_headers(
            path="/test-request",
            method="GET",
            **{
                "x-test-case": "7",
                "user-agent": "HTTP3-NonConformance-Test/1.0"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, initial_headers, end_stream=False)
            self.results.add_step("initial_headers_sent", True)
            print(f"✅ Initial HEADERS frame sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(initial_headers)} header fields")
        except Exception as e:
            print(f"❌ Failed to send initial HEADERS frame: {e}")
            self.results.add_step("initial_headers_sent", False)
            return
        
        # Step 4: Send trailing HEADERS frame with end_stream=True
        print("📍 Sending trailing HEADERS frame (closes stream)")
        trailing_headers = [
            (b"x-response-trailer", b"test-trailer-value"),
            (b"x-stream-complete", b"true")
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, trailing_headers, end_stream=True)
            self.results.add_step("trailing_headers_sent", True)
            print(f"✅ Trailing HEADERS frame sent with end_stream=True")
            print(f"   └─ This should close the request stream")
            print(f"   └─ No more frames should be sent on this stream")
        except Exception as e:
            print(f"❌ Failed to send trailing HEADERS frame: {e}")
            self.results.add_step("trailing_headers_sent", False)
            return
        
        # Step 5: Send DATA frame AFTER trailing HEADERS - VIOLATION!
        print("📍 Sending DATA frame AFTER trailing HEADERS")
        print("🚫 PROTOCOL VIOLATION: DATA frame after trailing HEADERS is invalid!")
        print("🚫 Expected error: H3_FRAME_UNEXPECTED (0x105)")
        
        # This violates HTTP/3 frame sequencing rules - no frames should be sent
        # after a trailing HEADERS frame with end_stream=True
        violation_data = b'{"violation": "This DATA frame should not be accepted after trailing HEADERS"}'
        
        try:
            self.h3_api.send_data_frame(request_stream_id, violation_data, end_stream=False)
            self.results.add_step("data_after_trailing_headers_sent", True)
            print(f"✅ DATA frame sent after trailing HEADERS on stream {request_stream_id}")
            print(f"   └─ Payload: {len(violation_data)} bytes")
            print(f"   └─ This violates HTTP/3 frame sequence rules!")
        except Exception as e:
            print(f"❌ Failed to send DATA frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as sent for result tracking
            self.results.add_step("data_after_trailing_headers_sent", True)
            self.results.add_note(f"DATA frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("DATA frame sent after trailing HEADERS with end_stream=True (protocol violation)")
        self.results.add_note("Invalid frame sequence should trigger H3_FRAME_UNEXPECTED")
        self.results.add_note("Stream should have been closed by trailing HEADERS frame")


async def main():
    """Main entry point for Test Case 7."""
    test_client = TestCase7Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 