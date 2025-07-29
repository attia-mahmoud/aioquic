#!/usr/bin/env python3

"""
Non-Conformance Test Case #25: Empty Path Pseudo-Header

Violates HTTP/3 specifications by sending the :path pseudo-header field 
with an empty value. The ':path' pseudo-header field MUST NOT be empty 
for 'http' or 'https' URIs; URIs that do not contain a path component 
MUST include a value of / (ASCII 0x2f).
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase25Client(BaseTestClient):
    """Test Case 25: Empty :path pseudo-header field."""
    
    def __init__(self):
        super().__init__(
            test_case_id=25,
            test_name="Empty :path pseudo-header field",
            violation_description=":path MUST NOT be empty for http/https URIs",
            rfc_section="HTTP/3 Path Pseudo-Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 25."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with empty :path - VIOLATION!
        print("📍 Sending HEADERS frame with empty :path pseudo-header")
        print("🚫 PROTOCOL VIOLATION: :path MUST NOT be empty for http/https URIs!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with empty :path pseudo-header
        # This violates HTTP/3 specification which requires :path to be non-empty
        violation_headers = [
            (b":method", b"GET"),
            (b":path", b""),  # FORBIDDEN: Empty :path value
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"25"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("empty_path_sent", True)
            print(f"✅ HEADERS frame with empty :path sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :path value: '' (empty string)")
            print(f"   └─ This violates HTTP/3 path field requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("empty_path_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with missing :path entirely
        print("📍 Sending second request without :path pseudo-header")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test completely missing :path pseudo-header
        violation_headers2 = [
            (b":method", b"POST"),
            # FORBIDDEN: Missing :path pseudo-header entirely
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"25"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("missing_path_sent", True)
            print(f"✅ Second HEADERS frame without :path sent on stream {request_stream_id2}")
            print(f"   └─ :path pseudo-header completely missing")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("missing_path_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "Request with empty :path pseudo-header", "path": ""}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "Request with missing :path pseudo-header", "path": null}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with empty/missing :path pseudo-header (protocol violation)")
        self.results.add_note(":path MUST NOT be empty for http/https URIs")
        self.results.add_note("URIs without path component MUST use :path value of '/'")
        self.results.add_note("Tested both empty string and missing :path pseudo-header")


async def main():
    """Main entry point for Test Case 25."""
    test_client = TestCase25Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 