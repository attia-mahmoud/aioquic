#!/usr/bin/env python3

"""
Non-Conformance Test Case #37: CONNECT Request with Path

Violates HTTP/3 specifications by sending a CONNECT request that includes 
a :path pseudo-header field. According to HTTP/3 specifications, a 
CONNECT request MUST be constructed with :method set to 'CONNECT' and 
the :path pseudo-header field MUST be omitted.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase37Client(BaseTestClient):
    """Test Case 37: CONNECT request with forbidden :path pseudo-header."""
    
    def __init__(self):
        super().__init__(
            test_case_id=37,
            test_name="CONNECT request with :path pseudo-header",
            violation_description="CONNECT requests MUST NOT include :path pseudo-header",
            rfc_section="HTTP/3 CONNECT Method Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 37."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send CONNECT request with :path - VIOLATION!
        print("📍 Sending CONNECT request with :path pseudo-header")
        print("🚫 PROTOCOL VIOLATION: CONNECT requests MUST NOT include :path!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create CONNECT request headers with forbidden :path pseudo-header
        # This violates HTTP/3 specification for CONNECT method requirements
        violation_headers = [
            (b":method", b"CONNECT"),
            (b":authority", b"example.com:443"),  # Required for CONNECT
            (b":path", b"/tunnel"),  # FORBIDDEN: :path in CONNECT request
            (b"x-test-case", b"37"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("connect_with_path_sent", True)
            print(f"✅ CONNECT request with :path sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :method: 'CONNECT'")
            print(f"   └─ :authority: 'example.com:443' (required)")
            print(f"   └─ :path: '/tunnel' (forbidden)")
            print(f"   └─ This violates HTTP/3 CONNECT method requirements!")
        except Exception as e:
            print(f"❌ Failed to send CONNECT request: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("connect_with_path_sent", True)
            self.results.add_note(f"CONNECT request sending failed: {str(e)}")
            return
        
        # Step 4: Send second CONNECT request with root path
        print("📍 Sending second CONNECT request with root path")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with root path
        violation_headers2 = [
            (b":method", b"CONNECT"),
            (b":authority", b"proxy.example.com:8080"),
            (b":path", b"/"),  # FORBIDDEN: Root path in CONNECT
            (b"x-test-case", b"37"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"proxy-authorization", b"Basic dGVzdDp0ZXN0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("connect_with_root_path_sent", True)
            print(f"✅ Second CONNECT request with root path sent on stream {request_stream_id2}")
            print(f"   └─ :path: '/' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send second CONNECT request: {e}")
            self.results.add_step("connect_with_root_path_sent", False)
            self.results.add_note(f"Second CONNECT request sending failed: {str(e)}")
        
        # Step 5: Send third CONNECT request with query parameters
        print("📍 Sending third CONNECT request with query parameters")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with query parameters in path
        violation_headers3 = [
            (b":method", b"CONNECT"),
            (b":authority", b"api.example.com:443"),
            (b":path", b"/connect?target=backend&port=5432"),  # FORBIDDEN: Path with query in CONNECT
            (b"x-test-case", b"37"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("connect_with_query_path_sent", True)
            print(f"✅ Third CONNECT request with query path sent on stream {request_stream_id3}")
            print(f"   └─ :path: '/connect?target=backend&port=5432' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send third CONNECT request: {e}")
            self.results.add_step("connect_with_query_path_sent", False)
            self.results.add_note(f"Third CONNECT request sending failed: {str(e)}")
        
        # Step 6: Send fourth CONNECT request with fragment
        print("📍 Sending fourth CONNECT request with fragment")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with fragment in path
        violation_headers4 = [
            (b":method", b"CONNECT"),
            (b":authority", b"websocket.example.com:80"),
            (b":path", b"/ws#connection"),  # FORBIDDEN: Path with fragment in CONNECT
            (b"x-test-case", b"37"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("connect_with_fragment_path_sent", True)
            print(f"✅ Fourth CONNECT request with fragment path sent on stream {request_stream_id4}")
            print(f"   └─ :path: '/ws#connection' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send fourth CONNECT request: {e}")
            self.results.add_step("connect_with_fragment_path_sent", False)
            self.results.add_note(f"Fourth CONNECT request sending failed: {str(e)}")
        
        # Step 7: Send fifth CONNECT request with empty path
        print("📍 Sending fifth CONNECT request with empty path")
        request_stream_id5 = self.create_request_stream(protocol)
        
        # Test with empty path value
        violation_headers5 = [
            (b":method", b"CONNECT"),
            (b":authority", b"empty-path.example.com:443"),
            (b":path", b""),  # FORBIDDEN: Empty path in CONNECT
            (b"x-test-case", b"37"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, violation_headers5, end_stream=False)
            self.results.add_step("connect_with_empty_path_sent", True)
            print(f"✅ Fifth CONNECT request with empty path sent on stream {request_stream_id5}")
            print(f"   └─ :path: '' (empty and forbidden)")
        except Exception as e:
            print(f"❌ Failed to send fifth CONNECT request: {e}")
            self.results.add_step("connect_with_empty_path_sent", False)
            self.results.add_note(f"Fifth CONNECT request sending failed: {str(e)}")
        
        # Step 8: Send sixth CONNECT request with duplicate paths
        print("📍 Sending sixth CONNECT request with duplicate paths")
        request_stream_id6 = self.create_request_stream(protocol)
        
        # Test with duplicate path headers (double violation)
        violation_headers6 = [
            (b":method", b"CONNECT"),
            (b":authority", b"duplicate.example.com:443"),
            (b":path", b"/tunnel1"),  # FORBIDDEN: First path in CONNECT
            (b":path", b"/tunnel2"),  # FORBIDDEN: Second path (duplicate)
            (b"x-test-case", b"37"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, violation_headers6, end_stream=False)
            self.results.add_step("connect_with_duplicate_paths_sent", True)
            print(f"✅ Sixth CONNECT request with duplicate paths sent on stream {request_stream_id6}")
            print(f"   └─ :path: '/tunnel1' + '/tunnel2' (duplicate and forbidden)")
        except Exception as e:
            print(f"❌ Failed to send sixth CONNECT request: {e}")
            self.results.add_step("connect_with_duplicate_paths_sent", False)
            self.results.add_note(f"Sixth CONNECT request sending failed: {str(e)}")
        
        # Step 9: Send seventh CONNECT request with absolute URI path
        print("📍 Sending seventh CONNECT request with absolute URI path")
        request_stream_id7 = self.create_request_stream(protocol)
        
        # Test with absolute URI in path (unusual but still forbidden)
        violation_headers7 = [
            (b":method", b"CONNECT"),
            (b":authority", b"absolute.example.com:443"),
            (b":path", b"https://target.example.com:443/resource"),  # FORBIDDEN: Absolute URI in path
            (b"x-test-case", b"37"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id7, violation_headers7, end_stream=False)
            self.results.add_step("connect_with_absolute_path_sent", True)
            print(f"✅ Seventh CONNECT request with absolute URI path sent on stream {request_stream_id7}")
            print(f"   └─ :path: 'https://target.example.com:443/resource' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send seventh CONNECT request: {e}")
            self.results.add_step("connect_with_absolute_path_sent", False)
            self.results.add_note(f"Seventh CONNECT request sending failed: {str(e)}")
        
        # Step 10: Send eighth CONNECT request with both :path and :scheme (compound violation)
        print("📍 Sending eighth CONNECT request with :path and :scheme")
        request_stream_id8 = self.create_request_stream(protocol)
        
        # Test with both forbidden :path and :scheme in CONNECT
        violation_headers8 = [
            (b":method", b"CONNECT"),
            (b":authority", b"compound.example.com:443"),
            (b":path", b"/secure-tunnel"),  # FORBIDDEN: path in CONNECT
            (b":scheme", b"https"),  # FORBIDDEN: scheme in CONNECT (separate violation)
            (b"x-test-case", b"37"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id8, violation_headers8, end_stream=False)
            self.results.add_step("connect_with_path_and_scheme_sent", True)
            print(f"✅ Eighth CONNECT request with :path and :scheme sent on stream {request_stream_id8}")
            print(f"   └─ :path: '/secure-tunnel' (forbidden)")
            print(f"   └─ :scheme: 'https' (also forbidden in CONNECT)")
        except Exception as e:
            print(f"❌ Failed to send eighth CONNECT request: {e}")
            self.results.add_step("connect_with_path_and_scheme_sent", False)
            self.results.add_note(f"Eighth CONNECT request sending failed: {str(e)}")
        
        # Step 11: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames for tunnel establishment")
        
        try:
            tunnel_data1 = b'CONNECT tunnel establishment with forbidden path'
            self.h3_api.send_data_frame(request_stream_id, tunnel_data1, end_stream=False)
            self.results.add_step("tunnel_data_1_sent", True)
            print(f"✅ First tunnel DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_1_sent", False)
        
        try:
            tunnel_data2 = b'Root path tunnel test data'
            self.h3_api.send_data_frame(request_stream_id2, tunnel_data2, end_stream=False)
            self.results.add_step("tunnel_data_2_sent", True)
            print(f"✅ Second tunnel DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_2_sent", False)
        
        try:
            tunnel_data3 = b'Query parameters tunnel data'
            self.h3_api.send_data_frame(request_stream_id3, tunnel_data3, end_stream=False)
            self.results.add_step("tunnel_data_3_sent", True)
            print(f"✅ Third tunnel DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_3_sent", False)
        
        try:
            tunnel_data4 = b'Fragment path tunnel establishment'
            self.h3_api.send_data_frame(request_stream_id4, tunnel_data4, end_stream=False)
            self.results.add_step("tunnel_data_4_sent", True)
            print(f"✅ Fourth tunnel DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_4_sent", False)
        
        try:
            tunnel_data5 = b'Empty path tunnel test'
            self.h3_api.send_data_frame(request_stream_id5, tunnel_data5, end_stream=False)
            self.results.add_step("tunnel_data_5_sent", True)
            print(f"✅ Fifth tunnel DATA frame sent on stream {request_stream_id5}")
        except Exception as e:
            print(f"❌ Failed to send fifth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_5_sent", False)
        
        try:
            tunnel_data6 = b'Duplicate paths tunnel data'
            self.h3_api.send_data_frame(request_stream_id6, tunnel_data6, end_stream=False)
            self.results.add_step("tunnel_data_6_sent", True)
            print(f"✅ Sixth tunnel DATA frame sent on stream {request_stream_id6}")
        except Exception as e:
            print(f"❌ Failed to send sixth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_6_sent", False)
        
        try:
            tunnel_data7 = b'Absolute URI path tunnel test'
            self.h3_api.send_data_frame(request_stream_id7, tunnel_data7, end_stream=False)
            self.results.add_step("tunnel_data_7_sent", True)
            print(f"✅ Seventh tunnel DATA frame sent on stream {request_stream_id7}")
        except Exception as e:
            print(f"❌ Failed to send seventh tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_7_sent", False)
        
        try:
            tunnel_data8 = b'Path and scheme violation tunnel'
            self.h3_api.send_data_frame(request_stream_id8, tunnel_data8, end_stream=False)
            self.results.add_step("tunnel_data_8_sent", True)
            print(f"✅ Eighth tunnel DATA frame sent on stream {request_stream_id8}")
        except Exception as e:
            print(f"❌ Failed to send eighth tunnel DATA frame: {e}")
            self.results.add_step("tunnel_data_8_sent", False)
        
        # Add test-specific observations
        self.results.add_note("CONNECT requests sent with forbidden :path pseudo-header (protocol violation)")
        self.results.add_note("CONNECT method MUST NOT include :path pseudo-header field")
        self.results.add_note("CONNECT is for tunneling; :path is for resource identification")
        self.results.add_note("Tested variations: normal path, root, query, fragment, empty, duplicate, absolute URI")
        self.results.add_note("Also tested combination with :scheme (separate CONNECT violation)")
        self.results.add_note("CONNECT requests should only have :method and :authority pseudo-headers")


async def main():
    """Main entry point for Test Case 37."""
    test_client = TestCase37Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 