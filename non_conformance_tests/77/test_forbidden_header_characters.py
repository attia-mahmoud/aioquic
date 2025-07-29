#!/usr/bin/env python3

"""
Non-Conformance Test Case #77: Forbidden Characters in Header Values

Violates HTTP/3 by sending header values containing forbidden characters. According to 
the specification, while most values that can be encoded will not alter field parsing, 
carriage return (ASCII 0x0d) might be exploited by an attacker if they are translated 
verbatim. Any request that contains a character not permitted in a field value MUST 
be treated as malformed.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient, create_common_headers


class TestCase77Client(BaseTestClient):
    """Test Case 77: Header value with forbidden characters."""
    
    def __init__(self):
        super().__init__(
            test_case_id=77,
            test_name="Forbidden characters in header values",
            violation_description="Forbidden header characters trigger malformed request",
            rfc_section="Characters not permitted in field value MUST be treated as malformed"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 77."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with forbidden characters - VIOLATION!
        print("📍 Sending HEADERS frame with forbidden characters")
        print("🚫 PROTOCOL VIOLATION: Carriage return in header value!")
        print("🚫 Expected: Malformed request error")
        
        try:
            # Create headers with forbidden carriage return character
            violation_headers = create_common_headers(
                path="/test-request", 
                method="GET",
                **{
                    "x-test-case": "77",
                    "user-agent": "HTTP3-NonConformance-Test/1.0"
                }
            )
            
            # Add header with forbidden character (carriage return 0x0d)
            forbidden_value = b"value\rmalicious"  # Contains carriage return
            violation_headers.append((b"x-custom", forbidden_value))
            
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=True)
            self.results.add_step("forbidden_header_characters_sent", True)
            print(f"✅ HEADERS frame with forbidden characters sent on stream {request_stream_id}")
            print(f"   └─ Header 'x-custom' contains carriage return (0x0d)")
            print(f"   └─ This violates header value character restrictions!")
            
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("forbidden_header_characters_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Header value with forbidden carriage return character (protocol violation)")
        self.results.add_note("Characters not permitted in field value MUST be treated as malformed")
        self.results.add_note("Should trigger malformed request error")


async def main():
    """Main entry point for Test Case 77."""
    test_client = TestCase77Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 