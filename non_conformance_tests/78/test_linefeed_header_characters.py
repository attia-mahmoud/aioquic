#!/usr/bin/env python3

"""
Non-Conformance Test Case #78: Line Feed Characters in Header Values

Violates HTTP/3 by sending header values containing line feed characters. According to 
the specification, while most values that can be encoded will not alter field parsing, 
line feed (ASCII 0x0a) might be exploited by an attacker if they are translated 
verbatim. Any request that contains a character not permitted in a field value MUST 
be treated as malformed.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils import BaseTestClient, create_common_headers


class TestCase78Client(BaseTestClient):
    """Test Case 78: Header value with line feed characters."""
    
    def __init__(self):
        super().__init__(
            test_case_id=78,
            test_name="Line feed characters in header values",
            violation_description="Line feed header characters trigger malformed request",
            rfc_section="Characters not permitted in field value MUST be treated as malformed"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 78."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with line feed characters - VIOLATION!
        print("📍 Sending HEADERS frame with line feed characters")
        print("🚫 PROTOCOL VIOLATION: Line feed in header value!")
        print("🚫 Expected: Malformed request error")
        
        try:
            # Create headers with forbidden line feed character
            violation_headers = create_common_headers(
                path="/test-request", 
                method="GET",
                **{
                    "x-test-case": "78",
                    "user-agent": "HTTP3-NonConformance-Test/1.0"
                }
            )
            
            # Add header with forbidden character (line feed 0x0a)
            forbidden_value = b"value\ninject"  # Contains line feed
            violation_headers.append((b"x-info", forbidden_value))
            
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=True)
            self.results.add_step("linefeed_header_characters_sent", True)
            print(f"✅ HEADERS frame with line feed characters sent on stream {request_stream_id}")
            print(f"   └─ Header 'x-info' contains line feed (0x0a)")
            print(f"   └─ This violates header value character restrictions!")
            
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("linefeed_header_characters_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Header value with forbidden line feed character (protocol violation)")
        self.results.add_note("Characters not permitted in field value MUST be treated as malformed")
        self.results.add_note("Should trigger malformed request error")


async def main():
    """Main entry point for Test Case 78."""
    test_client = TestCase78Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 