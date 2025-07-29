#!/usr/bin/env python3

"""
Non-Conformance Test Case #29: Missing Authority and Host Headers

Violates HTTP/3 specifications by sending an HTTPS request that contains 
neither an :authority pseudo-header field nor a Host header field. If the 
:scheme pseudo-header field identifies a scheme that has a mandatory 
authority component (including 'http' and 'https'), the request MUST 
contain either an :authority pseudo-header field or a Host header field.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase29Client(BaseTestClient):
    """Test Case 29: HTTPS request missing both :authority and Host headers."""
    
    def __init__(self):
        super().__init__(
            test_case_id=29,
            test_name="Missing :authority and Host headers",
            violation_description="HTTPS requests MUST contain either :authority or Host header",
            rfc_section="HTTP/3 Authority Component Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 29."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame without :authority or Host - VIOLATION!
        print("📍 Sending HTTPS request without :authority or Host header")
        print("🚫 PROTOCOL VIOLATION: HTTPS requests MUST contain either :authority or Host!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers missing both required authority indicators
        # This violates HTTP/3 specification for schemes with mandatory authority
        violation_headers = [
            (b":method", b"GET"),
            (b":path", b"/test-missing-authority-and-host"),
            (b":scheme", b"https"),  # Scheme requiring authority component
            # FORBIDDEN: Missing both :authority pseudo-header AND Host header
            (b"x-test-case", b"29"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("missing_authority_and_host_sent", True)
            print(f"✅ HEADERS frame without :authority or Host sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ Missing both :authority pseudo-header and Host header")
            print(f"   └─ This violates HTTP/3 authority requirements for HTTPS!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("missing_authority_and_host_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with HTTP scheme (also requires authority)
        print("📍 Sending second request with HTTP scheme without authority")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with HTTP scheme (also requires authority component)
        violation_headers2 = [
            (b":method", b"POST"),
            (b":path", b"/test-http-missing-authority"),
            (b":scheme", b"http"),  # HTTP also requires authority component
            # FORBIDDEN: Missing both :authority pseudo-header AND Host header
            (b"x-test-case", b"29"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("http_missing_authority_sent", True)
            print(f"✅ Second HEADERS frame (HTTP) without authority sent on stream {request_stream_id2}")
            print(f"   └─ HTTP scheme also requires authority component")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("http_missing_authority_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with empty :authority value
        print("📍 Sending third request with empty :authority pseudo-header")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with empty :authority pseudo-header value
        violation_headers3 = [
            (b":method", b"PUT"),
            (b":path", b"/test-empty-authority"),
            (b":scheme", b"https"),
            (b":authority", b""),  # FORBIDDEN: Empty :authority value
            (b"x-test-case", b"29"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("empty_authority_sent", True)
            print(f"✅ Third HEADERS frame with empty :authority sent on stream {request_stream_id3}")
            print(f"   └─ :authority value: '' (empty string)")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("empty_authority_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Send fourth test with empty Host header
        print("📍 Sending fourth request with empty Host header")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with empty Host header value
        violation_headers4 = [
            (b":method", b"DELETE"),
            (b":path", b"/test-empty-host"),
            (b":scheme", b"https"),
            (b"host", b""),  # FORBIDDEN: Empty Host header value
            (b"x-test-case", b"29"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("empty_host_sent", True)
            print(f"✅ Fourth HEADERS frame with empty Host header sent on stream {request_stream_id4}")
            print(f"   └─ Host header value: '' (empty string)")
        except Exception as e:
            print(f"❌ Failed to send fourth HEADERS frame: {e}")
            self.results.add_step("empty_host_sent", False)
            self.results.add_note(f"Fourth HEADERS frame sending failed: {str(e)}")
        
        # Step 7: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "HTTPS request without authority or host", "scheme": "https"}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "HTTP request without authority or host", "scheme": "http"}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        try:
            request_body3 = b'{"message": "HTTPS request with empty :authority", "authority": ""}'
            self.h3_api.send_data_frame(request_stream_id3, request_body3, end_stream=True)
            self.results.add_step("request_body_3_sent", True)
            print(f"✅ Third DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third DATA frame: {e}")
            self.results.add_step("request_body_3_sent", False)
        
        try:
            request_body4 = b'{"message": "HTTPS request with empty Host header", "host": ""}'
            self.h3_api.send_data_frame(request_stream_id4, request_body4, end_stream=True)
            self.results.add_step("request_body_4_sent", True)
            print(f"✅ Fourth DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth DATA frame: {e}")
            self.results.add_step("request_body_4_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent without required authority component (protocol violation)")
        self.results.add_note("HTTP/HTTPS schemes MUST contain either :authority or Host header")
        self.results.add_note("Tested missing both, empty :authority, and empty Host header")
        self.results.add_note("Authority component identifies the target server for the request")
        self.results.add_note("Valid authority: :authority pseudo-header OR Host header (but not both empty)")


async def main():
    """Main entry point for Test Case 29."""
    test_client = TestCase29Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 