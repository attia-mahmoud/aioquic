#!/usr/bin/env python3

"""
Non-Conformance Test Case #31: Empty Host Header

Violates HTTP/3 specifications by sending a request that includes the 
Host header field with an empty value. If the Host header field is 
present, it MUST NOT be empty.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase31Client(BaseTestClient):
    """Test Case 31: Request with empty Host header field."""
    
    def __init__(self):
        super().__init__(
            test_case_id=31,
            test_name="Empty Host header field",
            violation_description="Host header MUST NOT be empty when present",
            rfc_section="HTTP/3 Host Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 31."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with empty Host header - VIOLATION!
        print("📍 Sending HEADERS frame with empty Host header")
        print("🚫 PROTOCOL VIOLATION: Host header MUST NOT be empty when present!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with empty Host header
        # This violates HTTP/3 specification which prohibits empty Host header
        violation_headers = [
            (b":method", b"GET"),
            (b":path", b"/test-empty-host"),
            (b":scheme", b"https"),
            # Note: No :authority pseudo-header, using Host header instead
            (b"host", b""),  # FORBIDDEN: Empty Host header value
            (b"x-test-case", b"31"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("empty_host_sent", True)
            print(f"✅ HEADERS frame with empty Host header sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ Host header value: '' (empty string)")
            print(f"   └─ This violates HTTP/3 Host header requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("empty_host_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with whitespace-only Host header
        print("📍 Sending second request with whitespace-only Host header")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with whitespace-only Host header value
        violation_headers2 = [
            (b":method", b"POST"),
            (b":path", b"/test-whitespace-host"),
            (b":scheme", b"https"),
            (b"host", b"   "),  # FORBIDDEN: Whitespace-only Host header
            (b"x-test-case", b"31"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("whitespace_host_sent", True)
            print(f"✅ Second HEADERS frame with whitespace Host header sent on stream {request_stream_id2}")
            print(f"   └─ Host header value: '   ' (whitespace only)")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("whitespace_host_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with duplicate Host headers
        print("📍 Sending third request with duplicate Host headers")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with duplicate Host headers (first empty, second valid)
        violation_headers3 = [
            (b":method", b"PUT"),
            (b":path", b"/test-duplicate-host"),
            (b":scheme", b"https"),
            (b"host", b""),  # FORBIDDEN: Empty Host header
            (b"host", b"test-server"),  # FORBIDDEN: Duplicate Host header
            (b"x-test-case", b"31"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("duplicate_host_sent", True)
            print(f"✅ Third HEADERS frame with duplicate Host headers sent on stream {request_stream_id3}")
            print(f"   └─ First Host: '' (empty), Second Host: 'test-server'")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("duplicate_host_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Send fourth test with invalid characters in Host header
        print("📍 Sending fourth request with invalid characters in Host header")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with invalid characters in Host header
        violation_headers4 = [
            (b":method", b"DELETE"),
            (b":path", b"/test-invalid-host-chars"),
            (b":scheme", b"https"),
            (b"host", b"test\x00server\x01"),  # FORBIDDEN: Control characters in Host header
            (b"x-test-case", b"31"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("invalid_host_chars_sent", True)
            print(f"✅ Fourth HEADERS frame with invalid Host header chars sent on stream {request_stream_id4}")
            print(f"   └─ Host header contains control characters: \\x00 and \\x01")
        except Exception as e:
            print(f"❌ Failed to send fourth HEADERS frame: {e}")
            self.results.add_step("invalid_host_chars_sent", False)
            self.results.add_note(f"Fourth HEADERS frame sending failed: {str(e)}")
        
        # Step 7: Send fifth test with conflicting :authority and Host headers
        print("📍 Sending fifth request with conflicting :authority and Host headers")
        request_stream_id5 = self.create_request_stream(protocol)
        
        # Test with both :authority and Host header with different values
        violation_headers5 = [
            (b":method", b"PATCH"),
            (b":path", b"/test-conflicting-authority-host"),
            (b":scheme", b"https"),
            (b":authority", b"authority-server"),
            (b"host", b""),  # FORBIDDEN: Empty Host when :authority is present
            (b"x-test-case", b"31"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, violation_headers5, end_stream=False)
            self.results.add_step("conflicting_authority_host_sent", True)
            print(f"✅ Fifth HEADERS frame with conflicting authority/host sent on stream {request_stream_id5}")
            print(f"   └─ :authority: 'authority-server', Host: '' (empty)")
        except Exception as e:
            print(f"❌ Failed to send fifth HEADERS frame: {e}")
            self.results.add_step("conflicting_authority_host_sent", False)
            self.results.add_note(f"Fifth HEADERS frame sending failed: {str(e)}")
        
        # Step 8: Send sixth test with malformed Host header (invalid port)
        print("📍 Sending sixth request with malformed Host header (invalid port)")
        request_stream_id6 = self.create_request_stream(protocol)
        
        # Test with malformed Host header (invalid port number)
        violation_headers6 = [
            (b":method", b"OPTIONS"),
            (b":path", b"/test-malformed-host-port"),
            (b":scheme", b"https"),
            (b"host", b"test-server:99999"),  # FORBIDDEN: Invalid port number
            (b"x-test-case", b"31"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, violation_headers6, end_stream=False)
            self.results.add_step("malformed_host_port_sent", True)
            print(f"✅ Sixth HEADERS frame with malformed Host header port sent on stream {request_stream_id6}")
            print(f"   └─ Host header port: 99999 (exceeds valid range)")
        except Exception as e:
            print(f"❌ Failed to send sixth HEADERS frame: {e}")
            self.results.add_step("malformed_host_port_sent", False)
            self.results.add_note(f"Sixth HEADERS frame sending failed: {str(e)}")
        
        # Step 9: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "Request with empty Host header", "host": ""}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "Request with whitespace Host header", "host": "   "}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        try:
            request_body3 = b'{"message": "Request with duplicate Host headers", "hosts": ["", "test-server"]}'
            self.h3_api.send_data_frame(request_stream_id3, request_body3, end_stream=True)
            self.results.add_step("request_body_3_sent", True)
            print(f"✅ Third DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third DATA frame: {e}")
            self.results.add_step("request_body_3_sent", False)
        
        try:
            request_body4 = b'{"message": "Request with invalid Host header chars", "host": "test\\x00server\\x01"}'
            self.h3_api.send_data_frame(request_stream_id4, request_body4, end_stream=True)
            self.results.add_step("request_body_4_sent", True)
            print(f"✅ Fourth DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth DATA frame: {e}")
            self.results.add_step("request_body_4_sent", False)
        
        try:
            request_body5 = b'{"message": "Request with conflicting authority/host", "authority": "authority-server", "host": ""}'
            self.h3_api.send_data_frame(request_stream_id5, request_body5, end_stream=True)
            self.results.add_step("request_body_5_sent", True)
            print(f"✅ Fifth DATA frame sent on stream {request_stream_id5}")
        except Exception as e:
            print(f"❌ Failed to send fifth DATA frame: {e}")
            self.results.add_step("request_body_5_sent", False)
        
        try:
            request_body6 = b'{"message": "Request with malformed Host header port", "host": "test-server:99999"}'
            self.h3_api.send_data_frame(request_stream_id6, request_body6, end_stream=True)
            self.results.add_step("request_body_6_sent", True)
            print(f"✅ Sixth DATA frame sent on stream {request_stream_id6}")
        except Exception as e:
            print(f"❌ Failed to send sixth DATA frame: {e}")
            self.results.add_step("request_body_6_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with invalid Host header values (protocol violation)")
        self.results.add_note("Host header MUST NOT be empty when present")
        self.results.add_note("Tested empty, whitespace, duplicate, invalid chars, conflicting, and malformed port")
        self.results.add_note("Valid Host header format: host[:port] with proper encoding")
        self.results.add_note("Host header serves same purpose as :authority pseudo-header")


async def main():
    """Main entry point for Test Case 31."""
    test_client = TestCase31Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 