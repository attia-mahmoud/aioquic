#!/usr/bin/env python3

"""
Non-Conformance Test Case #24: Authority with Userinfo

Violates HTTP/3 specifications by sending the :authority pseudo-header 
field containing the deprecated userinfo subcomponent. The ':authority' 
pseudo-header field MUST NOT include userinfo for URIs of scheme 'http' 
or 'https'.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase24Client(BaseTestClient):
    """Test Case 24: :authority pseudo-header with userinfo component."""
    
    def __init__(self):
        super().__init__(
            test_case_id=24,
            test_name=":authority with userinfo component",
            violation_description=":authority MUST NOT include userinfo for http/https URIs",
            rfc_section="HTTP/3 Authority Pseudo-Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 24."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with :authority containing userinfo - VIOLATION!
        print("📍 Sending HEADERS frame with :authority containing userinfo")
        print("🚫 PROTOCOL VIOLATION: :authority MUST NOT include userinfo for http/https!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with forbidden userinfo in :authority
        # Userinfo format: [username[:password]@]host[:port]
        violation_headers = [
            (b":method", b"GET"),
            (b":path", b"/test-authority-userinfo"),
            (b":scheme", b"https"),
            # FORBIDDEN: :authority with userinfo (user:password@host)
            (b":authority", b"testuser:testpass@test-server:443"),  # Contains userinfo!
            (b"x-test-case", b"24"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"accept", b"application/json"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("authority_with_userinfo_sent", True)
            print(f"✅ HEADERS frame with userinfo in :authority sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :authority contains: testuser:testpass@test-server:443")
            print(f"   └─ This violates HTTP/3 authority field restrictions!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("authority_with_userinfo_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send additional test with different userinfo formats
        print("📍 Sending second request with different userinfo format")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with username only (no password)
        violation_headers2 = [
            (b":method", b"POST"),
            (b":path", b"/test-authority-userinfo-2"),
            (b":scheme", b"https"),
            # FORBIDDEN: :authority with username only
            (b":authority", b"admin@test-server"),  # Contains userinfo (username only)!
            (b"x-test-case", b"24"),
            (b"content-type", b"application/json"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("authority_with_username_only_sent", True)
            print(f"✅ Second HEADERS frame with username-only userinfo sent on stream {request_stream_id2}")
            print(f"   └─ :authority contains: admin@test-server")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("authority_with_username_only_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'{"message": "Request with userinfo in authority", "format": "user:pass@host"}'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"message": "Request with username-only userinfo in authority", "format": "user@host"}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with userinfo in :authority pseudo-header (protocol violation)")
        self.results.add_note(":authority MUST NOT include deprecated userinfo for http/https URIs")
        self.results.add_note("Tested formats: user:password@host and user@host")
        self.results.add_note("Valid :authority should only contain host[:port]")


async def main():
    """Main entry point for Test Case 24."""
    test_client = TestCase24Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 