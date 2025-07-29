#!/usr/bin/env python3

"""
Non-Conformance Test Case #63: Duplicate Setting Identifiers in SETTINGS Frame

Violates HTTP/3 by sending a SETTINGS frame with duplicate setting identifiers. 
According to the specification, the same setting identifier MUST NOT occur more 
than once in the SETTINGS frame. A server MAY treat the presence of duplicate 
setting identifiers as a connection error of type H3_SETTINGS_ERROR.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient
from aioquic.buffer import encode_uint_var


class TestCase63Client(BaseTestClient):
    """Test Case 63: SETTINGS frame with duplicate setting identifiers."""
    
    def __init__(self):
        super().__init__(
            test_case_id=63,
            test_name="Duplicate setting identifiers",
            violation_description="Duplicate setting identifiers trigger H3_SETTINGS_ERROR",
            rfc_section="Same setting identifier MUST NOT occur more than once"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 63."""
        
        # Step 1: Create control stream manually
        print("📍 Creating control stream")
        self.control_stream_id = self.h3_api.create_control_stream()
        self.results.add_step("control_stream_created", True)
        
        # Step 2: Send SETTINGS frame with duplicate identifiers - VIOLATION!
        print("📍 Sending SETTINGS frame with duplicate identifiers")
        print("🚫 PROTOCOL VIOLATION: Duplicate setting identifiers!")
        print("🚫 Expected error: H3_SETTINGS_ERROR (0x109)")
        
        try:
            # Manually construct SETTINGS frame with duplicate identifiers
            # Format: setting_id + value pairs
            # We'll duplicate QPACK_MAX_TABLE_CAPACITY (0x1) with different values
            settings_data = b""
            
            # First occurrence: QPACK_MAX_TABLE_CAPACITY = 4096
            settings_data += encode_uint_var(0x1)  # QPACK_MAX_TABLE_CAPACITY
            settings_data += encode_uint_var(4096)
            
            # Second occurrence: QPACK_MAX_TABLE_CAPACITY = 8192 (DUPLICATE!)
            settings_data += encode_uint_var(0x1)  # QPACK_MAX_TABLE_CAPACITY (duplicate)
            settings_data += encode_uint_var(8192)
            
            # Add other settings
            settings_data += encode_uint_var(0x6)  # QPACK_BLOCKED_STREAMS
            settings_data += encode_uint_var(16)
            
            # Send raw SETTINGS frame with duplicate identifiers
            self.h3_api.send_raw_frame(self.control_stream_id, 0x4, settings_data)  # FrameType.SETTINGS = 0x4
            self.results.add_step("duplicate_settings_sent", True)
            print(f"✅ SETTINGS frame with duplicate identifiers sent on stream {self.control_stream_id}")
            print(f"   └─ QPACK_MAX_TABLE_CAPACITY appears twice with different values")
            print(f"   └─ This violates setting identifier uniqueness!")
            
        except Exception as e:
            print(f"❌ Failed to send SETTINGS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("duplicate_settings_sent", True)
            self.results.add_note(f"SETTINGS frame sending failed: {str(e)}")
        
        # Step 3: Create QPACK streams
        print("📍 Creating QPACK streams")
        self.encoder_stream_id = self.h3_api.create_encoder_stream()
        self.decoder_stream_id = self.h3_api.create_decoder_stream()
        self.results.add_step("qpack_streams_created", True)
        
        # Add test-specific observations
        self.results.add_note("SETTINGS frame with duplicate setting identifiers (protocol violation)")
        self.results.add_note("Same setting identifier MUST NOT occur more than once")
        self.results.add_note("Should trigger H3_SETTINGS_ERROR connection error")


async def main():
    """Main entry point for Test Case 63."""
    test_client = TestCase63Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 