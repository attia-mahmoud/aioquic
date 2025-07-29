#!/usr/bin/env python3

"""
Non-Conformance Test Case #28: Missing Path Pseudo-Header

Violates HTTP/3 specifications by sending a request that omits the 
:path pseudo-header field. All HTTP/3 requests MUST include exactly 
one value for the :path pseudo-header field, unless the request is 
a CONNECT request.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase28Client(BaseTestClient):
    """Test Case 28: Request missing :path pseudo-header field."""
    
    def __init__(self):
        super().__init__(
            test_case_id=28,
            test_name="Missing :path pseudo-header field",
            violation_description=":path pseudo-header MUST be present in all HTTP/3 requests",
            rfc_section="HTTP/3 Request Pseudo-Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 28."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame without :path pseudo-header - VIOLATION!
        print("📍 Sending HEADERS frame without :path pseudo-header")
        print("🚫 PROTOCOL VIOLATION: :path pseudo-header MUST be present in HTTP/3 requests!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers missing the required :path pseudo-header
        # This violates HTTP/3 specification which requires :path in all requests
        violation_headers = [
            (b":method", b"GET"),
            # FORBIDDEN: Missing :path pseudo-header entirely
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"28"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("missing_path_headers_sent", True)
            print(f"✅ HEADERS frame without :path sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ Missing required :path pseudo-header")
            print(f"   └─ This violates HTTP/3 request requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("missing_path_headers_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with duplicate :path headers
        print("📍 Sending second request with duplicate :path pseudo-headers")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with duplicate :path pseudo-headers
        violation_headers2 = [
            (b":method", b"POST"),
            (b":path", b"/test-duplicate-path-1"),  # First :path
            (b":path", b"/test-duplicate-path-2"),  # FORBIDDEN: Duplicate :path
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"28"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("duplicate_path_headers_sent", True)
            print(f"✅ Second HEADERS frame with duplicate :path sent on stream {request_stream_id2}")
            print(f"   └─ Duplicate :path values: /test-duplicate-path-1 and /test-duplicate-path-2")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("duplicate_path_headers_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with malformed :path value
        print("📍 Sending third request with malformed :path pseudo-header")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with malformed :path pseudo-header value (contains spaces)
        violation_headers3 = [
            (b":method", b"PUT"),
            (b":path", b"/test path with spaces"),  # FORBIDDEN: Invalid path with spaces
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"28"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("malformed_path_headers_sent", True)
            print(f"✅ Third HEADERS frame with malformed :path sent on stream {request_stream_id3}")
            print(f"   └─ Malformed :path value: '/test path with spaces' (contains unencoded spaces)")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("malformed_path_headers_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Send fourth test with :path containing control characters
        print("📍 Sending fourth request with :path containing control characters")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with :path containing control characters
        violation_headers4 = [
            (b":method", b"DELETE"),
            (b":path", b"/test\x00\x01\x02"),  # FORBIDDEN: Path with control characters
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"28"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("control_char_path_headers_sent", True)
            print(f"✅ Fourth HEADERS frame with control characters in :path sent on stream {request_stream_id4}")
            print(f"   └─ :path contains control characters: \\x00\\x01\\x02")
        except Exception as e:
            print(f"❌ Failed to send fourth HEADERS frame: {e}")
            self.results.add_step("control_char_path_headers_sent", False)
            self.results.add_note(f"Fourth HEADERS frame sending failed: {str(e)}")
        
        # Step 7: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "Request without :path pseudo-header", "path": null}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "Request with duplicate :path pseudo-headers", "paths": ["/test-duplicate-path-1", "/test-duplicate-path-2"]}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        try:
            request_body3 = b'{"message": "Request with malformed :path pseudo-header", "path": "/test path with spaces"}'
            self.h3_api.send_data_frame(request_stream_id3, request_body3, end_stream=True)
            self.results.add_step("request_body_3_sent", True)
            print(f"✅ Third DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third DATA frame: {e}")
            self.results.add_step("request_body_3_sent", False)
        
        try:
            request_body4 = b'{"message": "Request with control characters in :path", "path": "/test\\x00\\x01\\x02"}'
            self.h3_api.send_data_frame(request_stream_id4, request_body4, end_stream=True)
            self.results.add_step("request_body_4_sent", True)
            print(f"✅ Fourth DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth DATA frame: {e}")
            self.results.add_step("request_body_4_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with missing/invalid :path pseudo-header (protocol violation)")
        self.results.add_note("All HTTP/3 requests MUST include exactly one :path pseudo-header")
        self.results.add_note("Tested missing :path, duplicate :path, malformed :path, and :path with control chars")
        self.results.add_note("Valid :path must be properly encoded URI path component")
        self.results.add_note("Exception: CONNECT requests may omit :path (not tested here)")


async def main():
    """Main entry point for Test Case 28."""
    test_client = TestCase28Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 