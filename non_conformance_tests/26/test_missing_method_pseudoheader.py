#!/usr/bin/env python3

"""
Non-Conformance Test Case #26: Missing Method Pseudo-Header

Violates HTTP/3 specifications by sending a request that omits the 
:method pseudo-header field. All HTTP/3 requests MUST include exactly 
one value for the :method pseudo-header field, unless the request is 
a CONNECT request.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase26Client(BaseTestClient):
    """Test Case 26: Request missing :method pseudo-header field."""
    
    def __init__(self):
        super().__init__(
            test_case_id=26,
            test_name="Missing :method pseudo-header field",
            violation_description=":method pseudo-header MUST be present in all HTTP/3 requests",
            rfc_section="HTTP/3 Request Pseudo-Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 26."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame without :method pseudo-header - VIOLATION!
        print("📍 Sending HEADERS frame without :method pseudo-header")
        print("🚫 PROTOCOL VIOLATION: :method pseudo-header MUST be present in HTTP/3 requests!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers missing the required :method pseudo-header
        # This violates HTTP/3 specification which requires :method in all requests
        violation_headers = [
            # FORBIDDEN: Missing :method pseudo-header entirely
            (b":path", b"/test-missing-method"),
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"26"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("missing_method_headers_sent", True)
            print(f"✅ HEADERS frame without :method sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ Missing required :method pseudo-header")
            print(f"   └─ This violates HTTP/3 request requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("missing_method_headers_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with empty :method value
        print("📍 Sending second request with empty :method pseudo-header")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with empty :method pseudo-header value
        violation_headers2 = [
            (b":method", b""),  # FORBIDDEN: Empty :method value
            (b":path", b"/test-empty-method"),
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"26"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("empty_method_headers_sent", True)
            print(f"✅ Second HEADERS frame with empty :method sent on stream {request_stream_id2}")
            print(f"   └─ :method value: '' (empty string)")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("empty_method_headers_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with duplicate :method headers
        print("📍 Sending third request with duplicate :method pseudo-headers")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with duplicate :method pseudo-headers
        violation_headers3 = [
            (b":method", b"GET"),  # First :method
            (b":method", b"POST"),  # FORBIDDEN: Duplicate :method
            (b":path", b"/test-duplicate-method"),
            (b":scheme", b"https"),
            (b":authority", b"test-server"),
            (b"x-test-case", b"26"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("duplicate_method_headers_sent", True)
            print(f"✅ Third HEADERS frame with duplicate :method sent on stream {request_stream_id3}")
            print(f"   └─ Duplicate :method values: GET and POST")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("duplicate_method_headers_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "Request without :method pseudo-header", "method": null}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "Request with empty :method pseudo-header", "method": ""}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        try:
            request_body3 = b'{"message": "Request with duplicate :method pseudo-headers", "methods": ["GET", "POST"]}'
            self.h3_api.send_data_frame(request_stream_id3, request_body3, end_stream=True)
            self.results.add_step("request_body_3_sent", True)
            print(f"✅ Third DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third DATA frame: {e}")
            self.results.add_step("request_body_3_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with missing/invalid :method pseudo-header (protocol violation)")
        self.results.add_note("All HTTP/3 requests MUST include exactly one :method pseudo-header")
        self.results.add_note("Tested missing :method, empty :method, and duplicate :method")
        self.results.add_note("Exception: CONNECT requests may omit :method (not tested here)")


async def main():
    """Main entry point for Test Case 26."""
    test_client = TestCase26Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 