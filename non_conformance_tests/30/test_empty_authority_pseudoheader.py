#!/usr/bin/env python3

"""
Non-Conformance Test Case #30: Empty Authority Pseudo-Header

Violates HTTP/3 specifications by sending a request that includes the 
:authority pseudo-header field with an empty value. If the :authority 
pseudo-header field is present, it MUST NOT be empty.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase30Client(BaseTestClient):
    """Test Case 30: Request with empty :authority pseudo-header field."""
    
    def __init__(self):
        super().__init__(
            test_case_id=30,
            test_name="Empty :authority pseudo-header field",
            violation_description=":authority pseudo-header MUST NOT be empty when present",
            rfc_section="HTTP/3 Authority Pseudo-Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 30."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with empty :authority - VIOLATION!
        print("📍 Sending HEADERS frame with empty :authority pseudo-header")
        print("🚫 PROTOCOL VIOLATION: :authority pseudo-header MUST NOT be empty when present!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with empty :authority pseudo-header
        # This violates HTTP/3 specification which prohibits empty :authority
        violation_headers = [
            (b":method", b"GET"),
            (b":path", b"/test-empty-authority"),
            (b":scheme", b"https"),
            (b":authority", b""),  # FORBIDDEN: Empty :authority value
            (b"x-test-case", b"30"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("empty_authority_sent", True)
            print(f"✅ HEADERS frame with empty :authority sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :authority value: '' (empty string)")
            print(f"   └─ This violates HTTP/3 authority requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("empty_authority_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with whitespace-only :authority
        print("📍 Sending second request with whitespace-only :authority")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with whitespace-only :authority pseudo-header value
        violation_headers2 = [
            (b":method", b"POST"),
            (b":path", b"/test-whitespace-authority"),
            (b":scheme", b"https"),
            (b":authority", b"   "),  # FORBIDDEN: Whitespace-only :authority
            (b"x-test-case", b"30"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("whitespace_authority_sent", True)
            print(f"✅ Second HEADERS frame with whitespace :authority sent on stream {request_stream_id2}")
            print(f"   └─ :authority value: '   ' (whitespace only)")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("whitespace_authority_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with duplicate :authority headers
        print("📍 Sending third request with duplicate :authority pseudo-headers")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with duplicate :authority pseudo-headers (first empty, second valid)
        violation_headers3 = [
            (b":method", b"PUT"),
            (b":path", b"/test-duplicate-authority"),
            (b":scheme", b"https"),
            (b":authority", b""),  # FORBIDDEN: Empty :authority
            (b":authority", b"test-server"),  # FORBIDDEN: Duplicate :authority
            (b"x-test-case", b"30"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("duplicate_authority_sent", True)
            print(f"✅ Third HEADERS frame with duplicate :authority sent on stream {request_stream_id3}")
            print(f"   └─ First :authority: '' (empty), Second :authority: 'test-server'")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("duplicate_authority_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Send fourth test with invalid characters in :authority
        print("📍 Sending fourth request with invalid characters in :authority")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with invalid characters in :authority
        violation_headers4 = [
            (b":method", b"DELETE"),
            (b":path", b"/test-invalid-authority-chars"),
            (b":scheme", b"https"),
            (b":authority", b"test\x00server\x01"),  # FORBIDDEN: Control characters in :authority
            (b"x-test-case", b"30"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("invalid_authority_chars_sent", True)
            print(f"✅ Fourth HEADERS frame with invalid :authority chars sent on stream {request_stream_id4}")
            print(f"   └─ :authority contains control characters: \\x00 and \\x01")
        except Exception as e:
            print(f"❌ Failed to send fourth HEADERS frame: {e}")
            self.results.add_step("invalid_authority_chars_sent", False)
            self.results.add_note(f"Fourth HEADERS frame sending failed: {str(e)}")
        
        # Step 7: Send fifth test with malformed authority (invalid port)
        print("📍 Sending fifth request with malformed :authority (invalid port)")
        request_stream_id5 = self.create_request_stream(protocol)
        
        # Test with malformed :authority (invalid port number)
        violation_headers5 = [
            (b":method", b"PATCH"),
            (b":path", b"/test-malformed-authority-port"),
            (b":scheme", b"https"),
            (b":authority", b"test-server:99999"),  # FORBIDDEN: Invalid port number
            (b"x-test-case", b"30"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, violation_headers5, end_stream=False)
            self.results.add_step("malformed_authority_port_sent", True)
            print(f"✅ Fifth HEADERS frame with malformed :authority port sent on stream {request_stream_id5}")
            print(f"   └─ :authority port: 99999 (exceeds valid range)")
        except Exception as e:
            print(f"❌ Failed to send fifth HEADERS frame: {e}")
            self.results.add_step("malformed_authority_port_sent", False)
            self.results.add_note(f"Fifth HEADERS frame sending failed: {str(e)}")
        
        # Step 8: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "Request with empty :authority", "authority": ""}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "Request with whitespace :authority", "authority": "   "}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        try:
            request_body3 = b'{"message": "Request with duplicate :authority", "authorities": ["", "test-server"]}'
            self.h3_api.send_data_frame(request_stream_id3, request_body3, end_stream=True)
            self.results.add_step("request_body_3_sent", True)
            print(f"✅ Third DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third DATA frame: {e}")
            self.results.add_step("request_body_3_sent", False)
        
        try:
            request_body4 = b'{"message": "Request with invalid :authority chars", "authority": "test\\x00server\\x01"}'
            self.h3_api.send_data_frame(request_stream_id4, request_body4, end_stream=True)
            self.results.add_step("request_body_4_sent", True)
            print(f"✅ Fourth DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth DATA frame: {e}")
            self.results.add_step("request_body_4_sent", False)
        
        try:
            request_body5 = b'{"message": "Request with malformed :authority port", "authority": "test-server:99999"}'
            self.h3_api.send_data_frame(request_stream_id5, request_body5, end_stream=True)
            self.results.add_step("request_body_5_sent", True)
            print(f"✅ Fifth DATA frame sent on stream {request_stream_id5}")
        except Exception as e:
            print(f"❌ Failed to send fifth DATA frame: {e}")
            self.results.add_step("request_body_5_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with invalid :authority pseudo-header values (protocol violation)")
        self.results.add_note(":authority pseudo-header MUST NOT be empty when present")
        self.results.add_note("Tested empty, whitespace, duplicate, invalid chars, and malformed port")
        self.results.add_note("Valid :authority format: host[:port] with proper encoding")
        self.results.add_note("Empty :authority is worse than missing :authority entirely")


async def main():
    """Main entry point for Test Case 30."""
    test_client = TestCase30Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 