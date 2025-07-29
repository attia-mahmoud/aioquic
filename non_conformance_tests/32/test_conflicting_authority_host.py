#!/usr/bin/env python3

"""
Non-Conformance Test Case #32: Conflicting Authority and Host Headers

Violates HTTP/3 specifications by sending a request that includes both 
the Host header field and the :authority pseudo-header field with 
different values. If both the Host header field and the :authority 
pseudo-header field are present, they MUST contain the same value.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase32Client(BaseTestClient):
    """Test Case 32: Request with conflicting :authority and Host headers."""
    
    def __init__(self):
        super().__init__(
            test_case_id=32,
            test_name="Conflicting :authority and Host headers",
            violation_description="Host and :authority MUST contain the same value when both present",
            rfc_section="HTTP/3 Authority Component Consistency Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 32."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with conflicting :authority and Host - VIOLATION!
        print("📍 Sending HEADERS frame with conflicting :authority and Host headers")
        print("🚫 PROTOCOL VIOLATION: Host and :authority MUST contain the same value!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with conflicting :authority and Host values
        # This violates HTTP/3 specification which requires them to match
        violation_headers = [
            (b":method", b"GET"),
            (b":path", b"/test-conflicting-authority-host"),
            (b":scheme", b"https"),
            (b":authority", b"authority-server.com"),  # First authority value
            (b"host", b"host-server.com"),  # FORBIDDEN: Different Host value
            (b"x-test-case", b"32"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("conflicting_authority_host_sent", True)
            print(f"✅ HEADERS frame with conflicting authority/host sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :authority: 'authority-server.com'")
            print(f"   └─ Host: 'host-server.com'")
            print(f"   └─ This violates HTTP/3 authority consistency requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("conflicting_authority_host_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with port mismatches
        print("📍 Sending second request with port mismatches")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with same hostname but different ports
        violation_headers2 = [
            (b":method", b"POST"),
            (b":path", b"/test-port-mismatch"),
            (b":scheme", b"https"),
            (b":authority", b"test-server.com:443"),  # Port 443
            (b"host", b"test-server.com:8443"),  # FORBIDDEN: Different port
            (b"x-test-case", b"32"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("port_mismatch_sent", True)
            print(f"✅ Second HEADERS frame with port mismatch sent on stream {request_stream_id2}")
            print(f"   └─ :authority: 'test-server.com:443'")
            print(f"   └─ Host: 'test-server.com:8443'")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("port_mismatch_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with case differences
        print("📍 Sending third request with case differences")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with case differences (should be normalized but might cause issues)
        violation_headers3 = [
            (b":method", b"PUT"),
            (b":path", b"/test-case-differences"),
            (b":scheme", b"https"),
            (b":authority", b"test-server.com"),  # Lowercase
            (b"host", b"TEST-SERVER.COM"),  # FORBIDDEN: Uppercase (case mismatch)
            (b"x-test-case", b"32"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("case_mismatch_sent", True)
            print(f"✅ Third HEADERS frame with case mismatch sent on stream {request_stream_id3}")
            print(f"   └─ :authority: 'test-server.com'")
            print(f"   └─ Host: 'TEST-SERVER.COM'")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("case_mismatch_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Send fourth test with subtle differences (trailing dot)
        print("📍 Sending fourth request with subtle differences (trailing dot)")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with subtle hostname differences
        violation_headers4 = [
            (b":method", b"DELETE"),
            (b":path", b"/test-subtle-differences"),
            (b":scheme", b"https"),
            (b":authority", b"test-server.com"),  # No trailing dot
            (b"host", b"test-server.com."),  # FORBIDDEN: Trailing dot difference
            (b"x-test-case", b"32"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("subtle_differences_sent", True)
            print(f"✅ Fourth HEADERS frame with subtle differences sent on stream {request_stream_id4}")
            print(f"   └─ :authority: 'test-server.com'")
            print(f"   └─ Host: 'test-server.com.'")
        except Exception as e:
            print(f"❌ Failed to send fourth HEADERS frame: {e}")
            self.results.add_step("subtle_differences_sent", False)
            self.results.add_note(f"Fourth HEADERS frame sending failed: {str(e)}")
        
        # Step 7: Send fifth test with IPv6 vs hostname mismatch
        print("📍 Sending fifth request with IPv6 vs hostname mismatch")
        request_stream_id5 = self.create_request_stream(protocol)
        
        # Test with IPv6 vs hostname mismatch
        violation_headers5 = [
            (b":method", b"PATCH"),
            (b":path", b"/test-ipv6-hostname-mismatch"),
            (b":scheme", b"https"),
            (b":authority", b"[::1]:443"),  # IPv6 address
            (b"host", b"localhost:443"),  # FORBIDDEN: Hostname (different representation)
            (b"x-test-case", b"32"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, violation_headers5, end_stream=False)
            self.results.add_step("ipv6_hostname_mismatch_sent", True)
            print(f"✅ Fifth HEADERS frame with IPv6/hostname mismatch sent on stream {request_stream_id5}")
            print(f"   └─ :authority: '[::1]:443'")
            print(f"   └─ Host: 'localhost:443'")
        except Exception as e:
            print(f"❌ Failed to send fifth HEADERS frame: {e}")
            self.results.add_step("ipv6_hostname_mismatch_sent", False)
            self.results.add_note(f"Fifth HEADERS frame sending failed: {str(e)}")
        
        # Step 8: Send sixth test with implicit vs explicit port
        print("📍 Sending sixth request with implicit vs explicit port")
        request_stream_id6 = self.create_request_stream(protocol)
        
        # Test with implicit vs explicit default port
        violation_headers6 = [
            (b":method", b"OPTIONS"),
            (b":path", b"/test-implicit-explicit-port"),
            (b":scheme", b"https"),
            (b":authority", b"test-server.com"),  # Implicit port 443 for HTTPS
            (b"host", b"test-server.com:443"),  # FORBIDDEN: Explicit port (technically same but different representation)
            (b"x-test-case", b"32"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, violation_headers6, end_stream=False)
            self.results.add_step("implicit_explicit_port_sent", True)
            print(f"✅ Sixth HEADERS frame with implicit/explicit port sent on stream {request_stream_id6}")
            print(f"   └─ :authority: 'test-server.com' (implicit port 443)")
            print(f"   └─ Host: 'test-server.com:443' (explicit port 443)")
        except Exception as e:
            print(f"❌ Failed to send sixth HEADERS frame: {e}")
            self.results.add_step("implicit_explicit_port_sent", False)
            self.results.add_note(f"Sixth HEADERS frame sending failed: {str(e)}")
        
        # Step 9: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "Conflicting authority and host", "authority": "authority-server.com", "host": "host-server.com"}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "Port mismatch", "authority": "test-server.com:443", "host": "test-server.com:8443"}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        try:
            request_body3 = b'{"message": "Case mismatch", "authority": "test-server.com", "host": "TEST-SERVER.COM"}'
            self.h3_api.send_data_frame(request_stream_id3, request_body3, end_stream=True)
            self.results.add_step("request_body_3_sent", True)
            print(f"✅ Third DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third DATA frame: {e}")
            self.results.add_step("request_body_3_sent", False)
        
        try:
            request_body4 = b'{"message": "Subtle differences", "authority": "test-server.com", "host": "test-server.com."}'
            self.h3_api.send_data_frame(request_stream_id4, request_body4, end_stream=True)
            self.results.add_step("request_body_4_sent", True)
            print(f"✅ Fourth DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth DATA frame: {e}")
            self.results.add_step("request_body_4_sent", False)
        
        try:
            request_body5 = b'{"message": "IPv6 vs hostname", "authority": "[::1]:443", "host": "localhost:443"}'
            self.h3_api.send_data_frame(request_stream_id5, request_body5, end_stream=True)
            self.results.add_step("request_body_5_sent", True)
            print(f"✅ Fifth DATA frame sent on stream {request_stream_id5}")
        except Exception as e:
            print(f"❌ Failed to send fifth DATA frame: {e}")
            self.results.add_step("request_body_5_sent", False)
        
        try:
            request_body6 = b'{"message": "Implicit vs explicit port", "authority": "test-server.com", "host": "test-server.com:443"}'
            self.h3_api.send_data_frame(request_stream_id6, request_body6, end_stream=True)
            self.results.add_step("request_body_6_sent", True)
            print(f"✅ Sixth DATA frame sent on stream {request_stream_id6}")
        except Exception as e:
            print(f"❌ Failed to send sixth DATA frame: {e}")
            self.results.add_step("request_body_6_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with conflicting Host and :authority values (protocol violation)")
        self.results.add_note("Host and :authority MUST contain the same value when both present")
        self.results.add_note("Tested hostname, port, case, subtle, IPv6/hostname, and implicit/explicit port mismatches")
        self.results.add_note("Authority consistency is critical for HTTP/3 request routing")
        self.results.add_note("Implementations should normalize and compare authority values consistently")


async def main():
    """Main entry point for Test Case 32."""
    test_client = TestCase32Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 