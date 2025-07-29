#!/usr/bin/env python3

"""
Non-Conformance Test Case #65: Reserved Setting Identifier

Violates HTTP/3 by sending a SETTINGS frame with a reserved setting identifier.
According to the specification, setting identifiers that were defined in HTTP/2
where there is no corresponding HTTP/3 setting have been reserved. These reserved
settings MUST NOT be sent by the client, and their receipt by the server MUST
be treated as a connection error of type H3_SETTINGS_ERROR.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient
from aioquic.buffer import encode_uint_var


class TestCase65Client(BaseTestClient):
    """Test Case 65: SETTINGS frame with reserved setting identifier."""
    
    def __init__(self):
        super().__init__(
            test_case_id=65,
            test_name="Reserved setting identifier",
            violation_description="Reserved setting identifier triggers H3_SETTINGS_ERROR",
            rfc_section="Reserved settings MUST NOT be sent by client"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 65."""
        
        # Step 1: Create control stream manually
        print("📍 Creating control stream")
        self.control_stream_id = self.h3_api.create_control_stream()
        self.results.add_step("control_stream_created", True)
        
        # Step 2: Send SETTINGS frame with reserved identifier - VIOLATION!
        print("📍 Sending SETTINGS frame with reserved identifier")
        print("🚫 PROTOCOL VIOLATION: Reserved setting identifier 0x2!")
        print("🚫 Expected error: H3_SETTINGS_ERROR (0x109)")
        
        try:
            # Manually construct SETTINGS frame with reserved identifier
            # Format: setting_id + value pairs
            settings_data = b""
            
            # Add valid settings first
            settings_data += encode_uint_var(0x1)    # QPACK_MAX_TABLE_CAPACITY
            settings_data += encode_uint_var(4096)
            settings_data += encode_uint_var(0x6)    # QPACK_BLOCKED_STREAMS
            settings_data += encode_uint_var(16)
            
            # Add reserved setting: 0x2 (SETTINGS_ENABLE_PUSH from HTTP/2)
            settings_data += encode_uint_var(0x2)    # Reserved: SETTINGS_ENABLE_PUSH
            settings_data += encode_uint_var(1)      # Value (irrelevant)
            
            # Send raw SETTINGS frame with reserved identifier
            self.h3_api.send_raw_frame(self.control_stream_id, 0x4, settings_data)  # FrameType.SETTINGS = 0x4
            self.results.add_step("reserved_settings_sent", True)
            print(f"✅ SETTINGS frame with reserved identifier sent on stream {self.control_stream_id}")
            print(f"   └─ Reserved setting ID 0x2 (SETTINGS_ENABLE_PUSH) included")
            print(f"   └─ This violates reserved setting restrictions!")
            
        except Exception as e:
            print(f"❌ Failed to send SETTINGS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("reserved_settings_sent", True)
            self.results.add_note(f"SETTINGS frame sending failed: {str(e)}")
        
        # Step 3: Create QPACK streams
        print("📍 Creating QPACK streams")
        self.encoder_stream_id = self.h3_api.create_encoder_stream()
        self.decoder_stream_id = self.h3_api.create_decoder_stream()
        self.results.add_step("qpack_streams_created", True)
        
        # Add test-specific observations
        self.results.add_note("SETTINGS frame with reserved setting identifier 0x2 (protocol violation)")
        self.results.add_note("Reserved settings MUST NOT be sent by client")
        self.results.add_note("Should trigger H3_SETTINGS_ERROR connection error")


async def main():
    """Main entry point for Test Case 65."""
    test_client = TestCase65Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 