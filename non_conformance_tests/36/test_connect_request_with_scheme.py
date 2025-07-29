#!/usr/bin/env python3

"""
Non-Conformance Test Case #36: CONNECT Request with Scheme

Violates HTTP/3 specifications by sending a CONNECT request that includes 
a :scheme pseudo-header field. According to HTTP/3 specifications, a 
CONNECT request MUST be constructed with :method set to 'CONNECT' and 
the :scheme pseudo-header field MUST be omitted.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase36Client(BaseTestClient):
    """Test Case 36: CONNECT request with forbidden :scheme pseudo-header."""
    
    def __init__(self):
        super().__init__(
            test_case_id=36,
            test_name="CONNECT request with :scheme pseudo-header",
            violation_description="CONNECT requests MUST NOT include :scheme pseudo-header",
            rfc_section="HTTP/3 CONNECT Method Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 36."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send CONNECT request with :scheme - VIOLATION!
        print("📍 Sending CONNECT request with :scheme pseudo-header")
        print("🚫 PROTOCOL VIOLATION: CONNECT requests MUST NOT include :scheme!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create CONNECT request headers with forbidden :scheme pseudo-header
        # This violates HTTP/3 specification for CONNECT method requirements
        violation_headers = [
            (b":method", b"CONNECT"),
            (b":authority", b"example.com:443"),  # Required for CONNECT
            (b":scheme", b"https"),  # FORBIDDEN: :scheme in CONNECT request
            (b"x-test-case", b"36"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("connect_with_scheme_sent", True)
            print(f"✅ CONNECT request with :scheme sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :method: 'CONNECT'")
            print(f"   └─ :authority: 'example.com:443' (required)")
            print(f"   └─ :scheme: 'https' (forbidden)")
            print(f"   └─ This violates HTTP/3 CONNECT method requirements!")
        except Exception as e:
            print(f"❌ Failed to send CONNECT request: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("connect_with_scheme_sent", True)
            self.results.add_note(f"CONNECT request sending failed: {str(e)}")
            return
        
        # Step 4: Send second CONNECT request with different scheme
        print("📍 Sending second CONNECT request with http scheme")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with different scheme value
        violation_headers2 = [
            (b":method", b"CONNECT"),
            (b":authority", b"proxy.example.com:8080"),
            (b":scheme", b"http"),  # FORBIDDEN: Different scheme in CONNECT
            (b"x-test-case", b"36"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"proxy-authorization", b"Basic dGVzdDp0ZXN0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("connect_with_http_scheme_sent", True)
            print(f"✅ Second CONNECT request with http scheme sent on stream {request_stream_id2}")
            print(f"   └─ :scheme: 'http' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send second CONNECT request: {e}")
            self.results.add_step("connect_with_http_scheme_sent", False)
            self.results.add_note(f"Second CONNECT request sending failed: {str(e)}")
        
        # Step 5: Send third CONNECT request with ws scheme (WebSocket)
        print("📍 Sending third CONNECT request with ws scheme")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with WebSocket scheme
        violation_headers3 = [
            (b":method", b"CONNECT"),
            (b":authority", b"websocket.example.com:80"),
            (b":scheme", b"ws"),  # FORBIDDEN: WebSocket scheme in CONNECT
            (b":protocol", b"websocket"),  # Valid for extended CONNECT
            (b"x-test-case", b"36"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("connect_with_ws_scheme_sent", True)
            print(f"✅ Third CONNECT request with ws scheme sent on stream {request_stream_id3}")
            print(f"   └─ :scheme: 'ws' (forbidden)")
            print(f"   └─ :protocol: 'websocket' (valid for extended CONNECT)")
        except Exception as e:
            print(f"❌ Failed to send third CONNECT request: {e}")
            self.results.add_step("connect_with_ws_scheme_sent", False)
            self.results.add_note(f"Third CONNECT request sending failed: {str(e)}")
        
        # Step 6: Send fourth CONNECT request with invalid scheme
        print("📍 Sending fourth CONNECT request with invalid scheme")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with completely invalid scheme
        violation_headers4 = [
            (b":method", b"CONNECT"),
            (b":authority", b"target.example.com:22"),
            (b":scheme", b"ssh"),  # FORBIDDEN: Non-HTTP scheme in CONNECT
            (b"x-test-case", b"36"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("connect_with_ssh_scheme_sent", True)
            print(f"✅ Fourth CONNECT request with ssh scheme sent on stream {request_stream_id4}")
            print(f"   └─ :scheme: 'ssh' (forbidden and invalid)")
        except Exception as e:
            print(f"❌ Failed to send fourth CONNECT request: {e}")
            self.results.add_step("connect_with_ssh_scheme_sent", False)
            self.results.add_note(f"Fourth CONNECT request sending failed: {str(e)}")
        
        # Step 7: Send fifth CONNECT request with empty scheme
        print("📍 Sending fifth CONNECT request with empty scheme")
        request_stream_id5 = self.create_request_stream(protocol)
        
        # Test with empty scheme value
        violation_headers5 = [
            (b":method", b"CONNECT"),
            (b":authority", b"empty-scheme.example.com:443"),
            (b":scheme", b""),  # FORBIDDEN: Empty scheme in CONNECT
            (b"x-test-case", b"36"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, violation_headers5, end_stream=False)
            self.results.add_step("connect_with_empty_scheme_sent", True)
            print(f"✅ Fifth CONNECT request with empty scheme sent on stream {request_stream_id5}")
            print(f"   └─ :scheme: '' (empty and forbidden)")
        except Exception as e:
            print(f"❌ Failed to send fifth CONNECT request: {e}")
            self.results.add_step("connect_with_empty_scheme_sent", False)
            self.results.add_note(f"Fifth CONNECT request sending failed: {str(e)}")
        
        # Step 8: Send sixth CONNECT request with duplicate schemes
        print("📍 Sending sixth CONNECT request with duplicate schemes")
        request_stream_id6 = self.create_request_stream(protocol)
        
        # Test with duplicate scheme headers (double violation)
        violation_headers6 = [
            (b":method", b"CONNECT"),
            (b":authority", b"duplicate.example.com:443"),
            (b":scheme", b"https"),  # FORBIDDEN: First scheme in CONNECT
            (b":scheme", b"http"),  # FORBIDDEN: Second scheme (duplicate)
            (b"x-test-case", b"36"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, violation_headers6, end_stream=False)
            self.results.add_step("connect_with_duplicate_schemes_sent", True)
            print(f"✅ Sixth CONNECT request with duplicate schemes sent on stream {request_stream_id6}")
            print(f"   └─ :scheme: 'https' + 'http' (duplicate and forbidden)")
        except Exception as e:
            print(f"❌ Failed to send sixth CONNECT request: {e}")
            self.results.add_step("connect_with_duplicate_schemes_sent", False)
            self.results.add_note(f"Sixth CONNECT request sending failed: {str(e)}")
        
        # Step 9: Send seventh CONNECT request with :path (another violation)
        print("📍 Sending seventh CONNECT request with :scheme and :path")
        request_stream_id7 = self.create_request_stream(protocol)
        
        # Test with both forbidden :scheme and :path in CONNECT
        violation_headers7 = [
            (b":method", b"CONNECT"),
            (b":authority", b"path-test.example.com:443"),
            (b":scheme", b"https"),  # FORBIDDEN: scheme in CONNECT
            (b":path", b"/tunnel"),  # FORBIDDEN: path in CONNECT (separate violation)
            (b"x-test-case", b"36"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id7, violation_headers7, end_stream=False)
            self.results.add_step("connect_with_scheme_and_path_sent", True)
            print(f"✅ Seventh CONNECT request with :scheme and :path sent on stream {request_stream_id7}")
            print(f"   └─ :scheme: 'https' (forbidden)")
            print(f"   └─ :path: '/tunnel' (also forbidden in CONNECT)")
        except Exception as e:
            print(f"❌ Failed to send seventh CONNECT request: {e}")
            self.results.add_step("connect_with_scheme_and_path_sent", False)
            self.results.add_note(f"Seventh CONNECT request sending failed: {str(e)}")
        
        # Step 10: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames for tunnel establishment")
        
        try:
            tunnel_data1 = b'CONNECT tunnel establishment data for HTTPS proxy'
            self.h3_api.send_data_frame(request_stream_id, tunnel_data1, end_stream=False)
            self.results.add_step("tunnel_data_1_sent", True)
            print(f"✅ First tunnel DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_1_sent", False)
        
        try:
            tunnel_data2 = b'HTTP proxy tunnel for target host connection'
            self.h3_api.send_data_frame(request_stream_id2, tunnel_data2, end_stream=False)
            self.results.add_step("tunnel_data_2_sent", True)
            print(f"✅ Second tunnel DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_2_sent", False)
        
        try:
            tunnel_data3 = b'WebSocket upgrade via CONNECT tunnel'
            self.h3_api.send_data_frame(request_stream_id3, tunnel_data3, end_stream=False)
            self.results.add_step("tunnel_data_3_sent", True)
            print(f"✅ Third tunnel DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_3_sent", False)
        
        try:
            tunnel_data4 = b'SSH tunnel establishment attempt'
            self.h3_api.send_data_frame(request_stream_id4, tunnel_data4, end_stream=False)
            self.results.add_step("tunnel_data_4_sent", True)
            print(f"✅ Fourth tunnel DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_4_sent", False)
        
        try:
            tunnel_data5 = b'Empty scheme tunnel test data'
            self.h3_api.send_data_frame(request_stream_id5, tunnel_data5, end_stream=False)
            self.results.add_step("tunnel_data_5_sent", True)
            print(f"✅ Fifth tunnel DATA frame sent on stream {request_stream_id5}")
        except Exception as e:
            print(f"❌ Failed to send fifth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_5_sent", False)
        
        try:
            tunnel_data6 = b'Duplicate scheme tunnel test'
            self.h3_api.send_data_frame(request_stream_id6, tunnel_data6, end_stream=False)
            self.results.add_step("tunnel_data_6_sent", True)
            print(f"✅ Sixth tunnel DATA frame sent on stream {request_stream_id6}")
        except Exception as e:
            print(f"❌ Failed to send sixth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_6_sent", False)
        
        try:
            tunnel_data7 = b'Scheme and path violation tunnel'
            self.h3_api.send_data_frame(request_stream_id7, tunnel_data7, end_stream=False)
            self.results.add_step("tunnel_data_7_sent", True)
            print(f"✅ Seventh tunnel DATA frame sent on stream {request_stream_id7}")
        except Exception as e:
            print(f"❌ Failed to send seventh tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_7_sent", False)
        
        # Add test-specific observations
        self.results.add_note("CONNECT requests sent with forbidden :scheme pseudo-header (protocol violation)")
        self.results.add_note("CONNECT method MUST NOT include :scheme pseudo-header field")
        self.results.add_note("CONNECT is for tunneling; :scheme is for resource identification")
        self.results.add_note("Tested variations: https, http, ws, ssh, empty, duplicate schemes")
        self.results.add_note("Also tested combination with :path (separate CONNECT violation)")
        self.results.add_note("CONNECT requests should only have :method and :authority pseudo-headers")


async def main():
    """Main entry point for Test Case 36."""
    test_client = TestCase36Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 