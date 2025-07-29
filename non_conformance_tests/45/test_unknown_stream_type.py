#!/usr/bin/env python3

"""
Non-Conformance Test Case #45: Unknown Stream Type

Tests server behavior when receiving an unknown unidirectional stream type.
The server MUST either abort reading or discard data without processing.
The client MUST NOT consider this a connection error.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient
from aioquic.buffer import encode_uint_var


class TestCase45Client(BaseTestClient):
    """Test Case 45: Unknown unidirectional stream type."""
    
    def __init__(self):
        super().__init__(
            test_case_id=45,
            test_name="Unknown unidirectional stream type",
            violation_description="Client opens unknown stream type, server should abort or discard",
            rfc_section="HTTP/3 Stream Type Handling"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 45."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create unknown unidirectional stream type
        print("📍 Creating unknown unidirectional stream")
        unknown_stream_type = 0xCC  # Unknown stream type
        
        try:
            # Get unidirectional stream ID
            stream_id = protocol._quic.get_next_available_stream_id(is_unidirectional=True)
            
            # Send unknown stream type identifier
            type_data = encode_uint_var(unknown_stream_type)
            protocol._quic.send_stream_data(stream_id, type_data)
            
            self.results.add_step("unknown_stream_created", True)
            print(f"✅ Unknown stream type {hex(unknown_stream_type)} created on stream {stream_id}")
            
        except Exception as e:
            print(f"❌ Failed to create unknown stream: {e}")
            self.results.add_step("unknown_stream_created", False)
            return
        
        # Step 3: Send some data on the unknown stream
        print("📍 Sending data on unknown stream")
        
        try:
            test_data = b"This is test data for unknown stream type"
            protocol._quic.send_stream_data(stream_id, test_data)
            
            self.results.add_step("data_sent", True)
            print(f"✅ Data sent on unknown stream: {len(test_data)} bytes")
            
        except Exception as e:
            print(f"❌ Failed to send data: {e}")
            self.results.add_step("data_sent", False)
        
        # Step 4: Wait and observe
        print("📍 Observing server behavior...")
        await asyncio.sleep(2.0)
        
        # Step 5: Test connection is still active
        print("📍 Testing connection state")
        
        try:
            request_stream_id = self.create_request_stream(protocol)
            headers = [
                (b":method", b"GET"),
                (b":path", b"/test"),
                (b":scheme", b"https"),
                (b":authority", b"localhost"),
                (b"x-test-case", b"45")
            ]
            
            self.h3_api.send_headers_frame(request_stream_id, headers, end_stream=True)
            self.results.add_step("connection_still_active", True)
            print(f"✅ Connection still active - normal request sent")
            
        except Exception as e:
            print(f"❌ Connection may be terminated: {e}")
            self.results.add_step("connection_still_active", False)
        
        # Add test observations
        self.results.add_note(f"Unknown stream type {hex(unknown_stream_type)} sent")
        self.results.add_note("Server should abort reading or discard data")
        self.results.add_note("Connection should remain active (not connection error)")


async def main():
    """Main entry point for Test Case 45."""
    test_client = TestCase45Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 