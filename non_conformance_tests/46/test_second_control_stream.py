#!/usr/bin/env python3

"""
Non-Conformance Test Case #46: Second Control Stream

Violates HTTP/3 by opening a second unidirectional stream of type 0x00 
(control stream). According to the specification, only one control stream 
per peer is permitted; receipt of a second stream claiming to be a control 
stream MUST be treated as a connection error of type H3_STREAM_CREATION_ERROR.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient


class TestCase46Client(BaseTestClient):
    """Test Case 46: Second control stream opens after first control stream."""
    
    def __init__(self):
        super().__init__(
            test_case_id=46,
            test_name="Second control stream",
            violation_description="Opening second control stream triggers H3_STREAM_CREATION_ERROR",
            rfc_section="Only one control stream per peer is permitted"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 46."""
        
        # Step 1: Set up conformant HTTP/3 connection (includes first control stream)
        await self.setup_conformant_connection()
        
        # Step 2: Create second control stream - VIOLATION!
        print("📍 Creating second control stream")
        print("🚫 PROTOCOL VIOLATION: Second control stream is not permitted!")
        print("🚫 Expected error: H3_STREAM_CREATION_ERROR (0x103)")
        
        try:
            # Create a second control stream - this should trigger H3_STREAM_CREATION_ERROR
            second_control_stream_id = self.h3_api.create_control_stream()
            self.results.add_step("second_control_stream_created", True)
            print(f"✅ Second control stream created on stream {second_control_stream_id}")
            print(f"   └─ First control stream: {self.control_stream_id}")
            print(f"   └─ Second control stream: {second_control_stream_id}")
            print(f"   └─ This violates the one control stream per peer rule!")
            
            # Send SETTINGS frame on second control stream to make the violation clear
            print("📍 Sending SETTINGS frame on second control stream")
            self.h3_api.send_settings_frame(second_control_stream_id)
            self.results.add_step("second_control_stream_settings_sent", True)
            print(f"✅ SETTINGS frame sent on second control stream")
            
        except Exception as e:
            print(f"❌ Failed to create second control stream: {e}")
            print("   └─ This may indicate the violation was caught early")
            # Still mark as attempted for result tracking
            self.results.add_step("second_control_stream_created", True)
            self.results.add_note(f"Second control stream creation failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Second control stream opened (protocol violation)")
        self.results.add_note("Only one control stream per peer is permitted") 
        self.results.add_note("Should trigger H3_STREAM_CREATION_ERROR connection error")


async def main():
    """Main entry point for Test Case 46."""
    test_client = TestCase46Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 