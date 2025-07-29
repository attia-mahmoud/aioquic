#!/usr/bin/env python3

"""
Non-Conformance Test Case #79: Null Characters in Header Values

Violates HTTP/3 by sending header values containing null characters. According to 
the specification, while most values that can be encoded will not alter field parsing, 
null character (ASCII 0x00) might be exploited by an attacker if they are translated 
verbatim. Any request that contains a character not permitted in a field value MUST 
be treated as malformed.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient, create_common_headers


class TestCase79Client(BaseTestClient):
    """Test Case 79: Header value with null characters."""
    
    def __init__(self):
        super().__init__(
            test_case_id=79,
            test_name="Null characters in header values",
            violation_description="Null header characters trigger malformed request",
            rfc_section="Characters not permitted in field value MUST be treated as malformed"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 79."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with null characters - VIOLATION!
        print("📍 Sending HEADERS frame with null characters")
        print("🚫 PROTOCOL VIOLATION: Null character in header value!")
        print("🚫 Expected: Malformed request error")
        
        try:
            # Create headers with forbidden null character
            violation_headers = create_common_headers(
                path="/test-request", 
                method="GET",
                **{
                    "x-test-case": "79",
                    "user-agent": "HTTP3-NonConformance-Test/1.0"
                }
            )
            
            # Add header with forbidden character (null 0x00)
            forbidden_value = b"name\x00admin"  # Contains null character
            violation_headers.append((b"x-user", forbidden_value))
            
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=True)
            self.results.add_step("null_header_characters_sent", True)
            print(f"✅ HEADERS frame with null characters sent on stream {request_stream_id}")
            print(f"   └─ Header 'x-user' contains null character (0x00)")
            print(f"   └─ This violates header value character restrictions!")
            
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("null_header_characters_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Header value with forbidden null character (protocol violation)")
        self.results.add_note("Characters not permitted in field value MUST be treated as malformed")
        self.results.add_note("Should trigger malformed request error")


async def main():
    """Main entry point for Test Case 79."""
    test_client = TestCase79Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 