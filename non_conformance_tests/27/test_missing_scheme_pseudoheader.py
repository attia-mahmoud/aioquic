#!/usr/bin/env python3

"""
Non-Conformance Test Case #27: Missing Scheme Pseudo-Header

Violates HTTP/3 specifications by sending a request that omits the 
:scheme pseudo-header field. All HTTP/3 requests MUST include exactly 
one value for the :scheme pseudo-header field, unless the request is 
a CONNECT request.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase27Client(BaseTestClient):
    """Test Case 27: Request missing :scheme pseudo-header field."""
    
    def __init__(self):
        super().__init__(
            test_case_id=27,
            test_name="Missing :scheme pseudo-header field",
            violation_description=":scheme pseudo-header MUST be present in all HTTP/3 requests",
            rfc_section="HTTP/3 Request Pseudo-Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 27."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame without :scheme pseudo-header - VIOLATION!
        print("📍 Sending HEADERS frame without :scheme pseudo-header")
        print("🚫 PROTOCOL VIOLATION: :scheme pseudo-header MUST be present in HTTP/3 requests!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers missing the required :scheme pseudo-header
        # This violates HTTP/3 specification which requires :scheme in all requests
        violation_headers = [
            (b":method", b"GET"),
            (b":path", b"/test-missing-scheme"),
            # FORBIDDEN: Missing :scheme pseudo-header entirely
            (b":authority", b"test-server"),
            (b"x-test-case", b"27"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("missing_scheme_headers_sent", True)
            print(f"✅ HEADERS frame without :scheme sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ Missing required :scheme pseudo-header")
            print(f"   └─ This violates HTTP/3 request requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("missing_scheme_headers_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with empty :scheme value
        print("📍 Sending second request with empty :scheme pseudo-header")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with empty :scheme pseudo-header value
        violation_headers2 = [
            (b":method", b"POST"),
            (b":path", b"/test-empty-scheme"),
            (b":scheme", b""),  # FORBIDDEN: Empty :scheme value
            (b":authority", b"test-server"),
            (b"x-test-case", b"27"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("empty_scheme_headers_sent", True)
            print(f"✅ Second HEADERS frame with empty :scheme sent on stream {request_stream_id2}")
            print(f"   └─ :scheme value: '' (empty string)")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("empty_scheme_headers_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with duplicate :scheme headers
        print("📍 Sending third request with duplicate :scheme pseudo-headers")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with duplicate :scheme pseudo-headers
        violation_headers3 = [
            (b":method", b"PUT"),
            (b":path", b"/test-duplicate-scheme"),
            (b":scheme", b"https"),  # First :scheme
            (b":scheme", b"http"),  # FORBIDDEN: Duplicate :scheme
            (b":authority", b"test-server"),
            (b"x-test-case", b"27"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("duplicate_scheme_headers_sent", True)
            print(f"✅ Third HEADERS frame with duplicate :scheme sent on stream {request_stream_id3}")
            print(f"   └─ Duplicate :scheme values: https and http")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("duplicate_scheme_headers_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Send fourth test with invalid :scheme value
        print("📍 Sending fourth request with invalid :scheme pseudo-header")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with invalid :scheme pseudo-header value
        violation_headers4 = [
            (b":method", b"DELETE"),
            (b":path", b"/test-invalid-scheme"),
            (b":scheme", b"ftp"),  # FORBIDDEN: Invalid scheme for HTTP/3
            (b":authority", b"test-server"),
            (b"x-test-case", b"27"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("invalid_scheme_headers_sent", True)
            print(f"✅ Fourth HEADERS frame with invalid :scheme sent on stream {request_stream_id4}")
            print(f"   └─ Invalid :scheme value: ftp (should be http or https)")
        except Exception as e:
            print(f"❌ Failed to send fourth HEADERS frame: {e}")
            self.results.add_step("invalid_scheme_headers_sent", False)
            self.results.add_note(f"Fourth HEADERS frame sending failed: {str(e)}")
        
        # Step 7: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "Request without :scheme pseudo-header", "scheme": null}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "Request with empty :scheme pseudo-header", "scheme": ""}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        try:
            request_body3 = b'{"message": "Request with duplicate :scheme pseudo-headers", "schemes": ["https", "http"]}'
            self.h3_api.send_data_frame(request_stream_id3, request_body3, end_stream=True)
            self.results.add_step("request_body_3_sent", True)
            print(f"✅ Third DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third DATA frame: {e}")
            self.results.add_step("request_body_3_sent", False)
        
        try:
            request_body4 = b'{"message": "Request with invalid :scheme pseudo-header", "scheme": "ftp"}'
            self.h3_api.send_data_frame(request_stream_id4, request_body4, end_stream=True)
            self.results.add_step("request_body_4_sent", True)
            print(f"✅ Fourth DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth DATA frame: {e}")
            self.results.add_step("request_body_4_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with missing/invalid :scheme pseudo-header (protocol violation)")
        self.results.add_note("All HTTP/3 requests MUST include exactly one :scheme pseudo-header")
        self.results.add_note("Tested missing :scheme, empty :scheme, duplicate :scheme, and invalid :scheme")
        self.results.add_note("Valid schemes for HTTP/3: http, https")
        self.results.add_note("Exception: CONNECT requests may omit :scheme (not tested here)")


async def main():
    """Main entry point for Test Case 27."""
    test_client = TestCase27Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 