#!/usr/bin/env python3

"""
Non-Conformance Test Case #38: CONNECT Request without Authority

Violates HTTP/3 specifications by sending a CONNECT request that omits 
the required :authority pseudo-header field. According to HTTP/3 
specifications, a CONNECT request MUST be constructed with :method set 
to 'CONNECT' and the :authority pseudo-header field MUST contain the 
host and port to connect to.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase38Client(BaseTestClient):
    """Test Case 38: CONNECT request without required :authority pseudo-header."""
    
    def __init__(self):
        super().__init__(
            test_case_id=38,
            test_name="CONNECT request without :authority pseudo-header",
            violation_description="CONNECT requests MUST include :authority pseudo-header",
            rfc_section="HTTP/3 CONNECT Method Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 38."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send CONNECT request without :authority - VIOLATION!
        print("📍 Sending CONNECT request without :authority pseudo-header")
        print("🚫 PROTOCOL VIOLATION: CONNECT requests MUST include :authority!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create CONNECT request headers without required :authority pseudo-header
        # This violates HTTP/3 specification for CONNECT method requirements
        violation_headers = [
            (b":method", b"CONNECT"),
            # Missing :authority field - VIOLATION!
            (b"x-test-case", b"38"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("connect_without_authority_sent", True)
            print(f"✅ CONNECT request without :authority sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :method: 'CONNECT'")
            print(f"   └─ :authority: MISSING (required)")
            print(f"   └─ This violates HTTP/3 CONNECT method requirements!")
        except Exception as e:
            print(f"❌ Failed to send CONNECT request: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("connect_without_authority_sent", True)
            self.results.add_note(f"CONNECT request sending failed: {str(e)}")
            return
        
        # Step 4: Send second CONNECT request with empty :authority
        print("📍 Sending second CONNECT request with empty :authority")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with empty authority value (also a violation)
        violation_headers2 = [
            (b":method", b"CONNECT"),
            (b":authority", b""),  # Empty authority - effectively missing
            (b"x-test-case", b"38"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"proxy-authorization", b"Basic dGVzdDp0ZXN0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("connect_with_empty_authority_sent", True)
            print(f"✅ Second CONNECT request with empty :authority sent on stream {request_stream_id2}")
            print(f"   └─ :authority: '' (empty, effectively missing)")
        except Exception as e:
            print(f"❌ Failed to send second CONNECT request: {e}")
            self.results.add_step("connect_with_empty_authority_sent", False)
            self.results.add_note(f"Second CONNECT request sending failed: {str(e)}")
        
        # Step 5: Send third CONNECT request with only forbidden headers
        print("📍 Sending third CONNECT request with forbidden headers but no :authority")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with forbidden headers but missing required :authority
        violation_headers3 = [
            (b":method", b"CONNECT"),
            (b":scheme", b"https"),  # FORBIDDEN in CONNECT
            (b":path", b"/tunnel"),  # FORBIDDEN in CONNECT
            # Missing :authority field - VIOLATION!
            (b"x-test-case", b"38"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("connect_forbidden_headers_no_authority_sent", True)
            print(f"✅ Third CONNECT request with forbidden headers but no :authority sent on stream {request_stream_id3}")
            print(f"   └─ :scheme: 'https' (forbidden)")
            print(f"   └─ :path: '/tunnel' (forbidden)")
            print(f"   └─ :authority: MISSING (required)")
        except Exception as e:
            print(f"❌ Failed to send third CONNECT request: {e}")
            self.results.add_step("connect_forbidden_headers_no_authority_sent", False)
            self.results.add_note(f"Third CONNECT request sending failed: {str(e)}")
        
        # Step 6: Send fourth CONNECT request with Host header but no :authority
        print("📍 Sending fourth CONNECT request with Host header but no :authority")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with Host header instead of :authority (not equivalent for CONNECT)
        violation_headers4 = [
            (b":method", b"CONNECT"),
            (b"host", b"example.com:443"),  # Host header doesn't replace :authority for CONNECT
            # Missing :authority field - VIOLATION!
            (b"x-test-case", b"38"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("connect_host_header_no_authority_sent", True)
            print(f"✅ Fourth CONNECT request with Host but no :authority sent on stream {request_stream_id4}")
            print(f"   └─ Host: 'example.com:443' (not equivalent to :authority for CONNECT)")
            print(f"   └─ :authority: MISSING (required)")
        except Exception as e:
            print(f"❌ Failed to send fourth CONNECT request: {e}")
            self.results.add_step("connect_host_header_no_authority_sent", False)
            self.results.add_note(f"Fourth CONNECT request sending failed: {str(e)}")
        
        # Step 7: Send fifth CONNECT request with whitespace-only :authority
        print("📍 Sending fifth CONNECT request with whitespace-only :authority")
        request_stream_id5 = self.create_request_stream(protocol)
        
        # Test with whitespace-only authority (effectively empty)
        violation_headers5 = [
            (b":method", b"CONNECT"),
            (b":authority", b"   "),  # Whitespace-only authority
            (b"x-test-case", b"38"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, violation_headers5, end_stream=False)
            self.results.add_step("connect_whitespace_authority_sent", True)
            print(f"✅ Fifth CONNECT request with whitespace :authority sent on stream {request_stream_id5}")
            print(f"   └─ :authority: '   ' (whitespace-only, effectively missing)")
        except Exception as e:
            print(f"❌ Failed to send fifth CONNECT request: {e}")
            self.results.add_step("connect_whitespace_authority_sent", False)
            self.results.add_note(f"Fifth CONNECT request sending failed: {str(e)}")
        
        # Step 8: Send sixth CONNECT request with malformed :authority
        print("📍 Sending sixth CONNECT request with malformed :authority")
        request_stream_id6 = self.create_request_stream(protocol)
        
        # Test with malformed authority value
        violation_headers6 = [
            (b":method", b"CONNECT"),
            (b":authority", b"not-a-valid-host:port"),  # Malformed authority
            (b"x-test-case", b"38"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, violation_headers6, end_stream=False)
            self.results.add_step("connect_malformed_authority_sent", True)
            print(f"✅ Sixth CONNECT request with malformed :authority sent on stream {request_stream_id6}")
            print(f"   └─ :authority: 'not-a-valid-host:port' (malformed)")
        except Exception as e:
            print(f"❌ Failed to send sixth CONNECT request: {e}")
            self.results.add_step("connect_malformed_authority_sent", False)
            self.results.add_note(f"Sixth CONNECT request sending failed: {str(e)}")
        
        # Step 9: Send seventh CONNECT request with only method
        print("📍 Sending seventh CONNECT request with only :method")
        request_stream_id7 = self.create_request_stream(protocol)
        
        # Test with minimal headers (only method, no authority)
        violation_headers7 = [
            (b":method", b"CONNECT"),
            # Absolutely minimal - only method, no other headers
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id7, violation_headers7, end_stream=False)
            self.results.add_step("connect_only_method_sent", True)
            print(f"✅ Seventh CONNECT request with only :method sent on stream {request_stream_id7}")
            print(f"   └─ Headers: Only :method, no :authority")
        except Exception as e:
            print(f"❌ Failed to send seventh CONNECT request: {e}")
            self.results.add_step("connect_only_method_sent", False)
            self.results.add_note(f"Seventh CONNECT request sending failed: {str(e)}")
        
        # Step 10: Send eighth CONNECT request with invalid :authority format
        print("📍 Sending eighth CONNECT request with invalid :authority format")
        request_stream_id8 = self.create_request_stream(protocol)
        
        # Test with invalid authority format (missing port)
        violation_headers8 = [
            (b":method", b"CONNECT"),
            (b":authority", b"just-hostname-no-port"),  # Missing port for CONNECT
            (b"x-test-case", b"38"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id8, violation_headers8, end_stream=False)
            self.results.add_step("connect_invalid_authority_format_sent", True)
            print(f"✅ Eighth CONNECT request with invalid :authority format sent on stream {request_stream_id8}")
            print(f"   └─ :authority: 'just-hostname-no-port' (missing port)")
        except Exception as e:
            print(f"❌ Failed to send eighth CONNECT request: {e}")
            self.results.add_step("connect_invalid_authority_format_sent", False)
            self.results.add_note(f"Eighth CONNECT request sending failed: {str(e)}")
        
        # Step 11: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames for tunnel establishment")
        
        try:
            tunnel_data1 = b'CONNECT tunnel data without destination authority'
            self.h3_api.send_data_frame(request_stream_id, tunnel_data1, end_stream=False)
            self.results.add_step("tunnel_data_1_sent", True)
            print(f"✅ First tunnel DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_1_sent", False)
        
        try:
            tunnel_data2 = b'Empty authority tunnel test'
            self.h3_api.send_data_frame(request_stream_id2, tunnel_data2, end_stream=False)
            self.results.add_step("tunnel_data_2_sent", True)
            print(f"✅ Second tunnel DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_2_sent", False)
        
        try:
            tunnel_data3 = b'Forbidden headers no authority tunnel'
            self.h3_api.send_data_frame(request_stream_id3, tunnel_data3, end_stream=False)
            self.results.add_step("tunnel_data_3_sent", True)
            print(f"✅ Third tunnel DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_3_sent", False)
        
        try:
            tunnel_data4 = b'Host header instead of authority'
            self.h3_api.send_data_frame(request_stream_id4, tunnel_data4, end_stream=False)
            self.results.add_step("tunnel_data_4_sent", True)
            print(f"✅ Fourth tunnel DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_4_sent", False)
        
        try:
            tunnel_data5 = b'Whitespace authority tunnel test'
            self.h3_api.send_data_frame(request_stream_id5, tunnel_data5, end_stream=False)
            self.results.add_step("tunnel_data_5_sent", True)
            print(f"✅ Fifth tunnel DATA frame sent on stream {request_stream_id5}")
        except Exception as e:
            print(f"❌ Failed to send fifth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_5_sent", False)
        
        try:
            tunnel_data6 = b'Malformed authority tunnel data'
            self.h3_api.send_data_frame(request_stream_id6, tunnel_data6, end_stream=False)
            self.results.add_step("tunnel_data_6_sent", True)
            print(f"✅ Sixth tunnel DATA frame sent on stream {request_stream_id6}")
        except Exception as e:
            print(f"❌ Failed to send sixth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_6_sent", False)
        
        try:
            tunnel_data7 = b'Method-only tunnel establishment'
            self.h3_api.send_data_frame(request_stream_id7, tunnel_data7, end_stream=False)
            self.results.add_step("tunnel_data_7_sent", True)
            print(f"✅ Seventh tunnel DATA frame sent on stream {request_stream_id7}")
        except Exception as e:
            print(f"❌ Failed to send seventh tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_7_sent", False)
        
        try:
            tunnel_data8 = b'Invalid authority format tunnel'
            self.h3_api.send_data_frame(request_stream_id8, tunnel_data8, end_stream=False)
            self.results.add_step("tunnel_data_8_sent", True)
            print(f"✅ Eighth tunnel DATA frame sent on stream {request_stream_id8}")
        except Exception as e:
            print(f"❌ Failed to send eighth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_8_sent", False)
        
        # Add test-specific observations
        self.results.add_note("CONNECT requests sent without required :authority pseudo-header (protocol violation)")
        self.results.add_note("CONNECT method MUST include :authority pseudo-header field")
        self.results.add_note("Authority specifies tunnel destination; without it, tunnel cannot be established")
        self.results.add_note("Tested variations: missing, empty, whitespace, malformed, invalid format")
        self.results.add_note("Host header cannot substitute for :authority in CONNECT requests")
        self.results.add_note("CONNECT requires exactly :method and :authority pseudo-headers")


async def main():
    """Main entry point for Test Case 38."""
    test_client = TestCase38Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 