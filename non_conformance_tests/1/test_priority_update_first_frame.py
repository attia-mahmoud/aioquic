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

from utils import BaseTestClient, create_common_headers


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
        
        # Step 1: Create control stream (conformant)
        print("📍 Creating control stream")
        self.control_stream_id = self.h3_api.create_control_stream()
        self.results.add_step("control_stream_created", True)
        
        # Step 2: Send PRIORITY_UPDATE as first frame (VIOLATION!)
        print("📍 Sending PRIORITY_UPDATE as FIRST frame")
        print("🚫 PROTOCOL VIOLATION: SETTINGS frame should be first!")
        self.h3_api.send_priority_update_frame(
            stream_id=self.control_stream_id,
            prioritized_element_id=0,
            priority_field=b"i"
        )
        self.results.add_step("priority_update_sent", True)
        print(f"✅ PRIORITY_UPDATE sent on stream {self.control_stream_id}")
        
        # Step 3: Create QPACK streams
        print("📍 Creating QPACK streams")
        self.encoder_stream_id = self.h3_api.create_encoder_stream()
        self.decoder_stream_id = self.h3_api.create_decoder_stream()
        self.results.add_step("qpack_streams_created", True)
        
        # Step 4: Send HTTP request (to see if connection works)
        print("📍 Sending HTTP request")
        request_stream_id = self.create_request_stream(protocol)
        headers = create_common_headers(path="/test-case-1")
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, headers, end_stream=True)
            self.results.add_step("request_sent", True)
            print(f"✅ HTTP request sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
            self.results.add_note(f"Request failed: {str(e)}")
        
        # Step 5: Send SETTINGS frame late (still non-conformant)
        print("📍 Sending SETTINGS frame (late)")
        print("🚫 STILL NON-CONFORMANT: Should have been first frame")
        self.h3_api.send_settings_frame(self.control_stream_id)
        self.results.add_step("settings_sent_late", True)
        print("✅ SETTINGS frame sent (but violates 'first frame' requirement)")
        
        # Add test-specific observations
        self.results.add_note("PRIORITY_UPDATE was sent as first frame (protocol violation)")
        self.results.add_note("SETTINGS frame was sent later (still non-conformant)")


async def main():
    """Main entry point for Test Case 1."""
    test_client = TestCase1Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 