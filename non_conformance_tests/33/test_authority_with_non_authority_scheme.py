#!/usr/bin/env python3

"""
Non-Conformance Test Case #33: Authority with Non-Authority Scheme

Violates HTTP/3 specifications by sending a request with a scheme that 
does not have a mandatory authority component (like 'mailto:') but 
includes an :authority pseudo-header field. If the scheme does not have 
a mandatory authority component and none is provided in the request 
target, the request MUST NOT contain the :authority pseudo-header.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase33Client(BaseTestClient):
    """Test Case 33: Request with :authority for non-authority schemes."""
    
    def __init__(self):
        super().__init__(
            test_case_id=33,
            test_name="Authority with non-authority scheme",
            violation_description="Non-authority schemes MUST NOT contain :authority pseudo-header",
            rfc_section="HTTP/3 Scheme-Specific Authority Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 33."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with mailto scheme + :authority - VIOLATION!
        print("📍 Sending HEADERS frame with mailto scheme and :authority")
        print("🚫 PROTOCOL VIOLATION: Non-authority schemes MUST NOT contain :authority!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with mailto scheme (no authority component) but include :authority
        # This violates HTTP/3 specification for scheme-authority consistency
        violation_headers = [
            (b":method", b"POST"),
            (b":path", b"user@example.com"),  # mailto path format
            (b":scheme", b"mailto"),  # Scheme without mandatory authority
            (b":authority", b"mail-server.com"),  # FORBIDDEN: :authority with non-authority scheme
            (b"x-test-case", b"33"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"content-type", b"message/rfc822"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("mailto_with_authority_sent", True)
            print(f"✅ HEADERS frame with mailto + :authority sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :scheme: 'mailto' (no authority component)")
            print(f"   └─ :authority: 'mail-server.com' (forbidden)")
            print(f"   └─ This violates HTTP/3 scheme-authority requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("mailto_with_authority_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with file scheme + :authority
        print("📍 Sending second request with file scheme and :authority")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with file scheme (also no authority component)
        violation_headers2 = [
            (b":method", b"GET"),
            (b":path", b"/etc/passwd"),  # file path
            (b":scheme", b"file"),  # Scheme without mandatory authority
            (b":authority", b"localhost"),  # FORBIDDEN: :authority with file scheme
            (b"x-test-case", b"33"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("file_with_authority_sent", True)
            print(f"✅ Second HEADERS frame with file + :authority sent on stream {request_stream_id2}")
            print(f"   └─ :scheme: 'file' (no authority component)")
            print(f"   └─ :authority: 'localhost' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("file_with_authority_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with data scheme + :authority
        print("📍 Sending third request with data scheme and :authority")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with data scheme (inline data, no authority)
        violation_headers3 = [
            (b":method", b"GET"),
            (b":path", b"text/plain;charset=utf-8,Hello%20World"),  # data URI path
            (b":scheme", b"data"),  # Scheme without mandatory authority
            (b":authority", b"data-server.com"),  # FORBIDDEN: :authority with data scheme
            (b"x-test-case", b"33"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("data_with_authority_sent", True)
            print(f"✅ Third HEADERS frame with data + :authority sent on stream {request_stream_id3}")
            print(f"   └─ :scheme: 'data' (no authority component)")
            print(f"   └─ :authority: 'data-server.com' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("data_with_authority_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Send fourth test with tel scheme + :authority
        print("📍 Sending fourth request with tel scheme and :authority")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with tel scheme (telephone numbers, no authority)
        violation_headers4 = [
            (b":method", b"GET"),
            (b":path", b"+1-800-555-0123"),  # telephone number path
            (b":scheme", b"tel"),  # Scheme without mandatory authority
            (b":authority", b"telecom-provider.com"),  # FORBIDDEN: :authority with tel scheme
            (b"x-test-case", b"33"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("tel_with_authority_sent", True)
            print(f"✅ Fourth HEADERS frame with tel + :authority sent on stream {request_stream_id4}")
            print(f"   └─ :scheme: 'tel' (no authority component)")
            print(f"   └─ :authority: 'telecom-provider.com' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send fourth HEADERS frame: {e}")
            self.results.add_step("tel_with_authority_sent", False)
            self.results.add_note(f"Fourth HEADERS frame sending failed: {str(e)}")
        
        # Step 7: Send fifth test with urn scheme + :authority
        print("📍 Sending fifth request with urn scheme and :authority")
        request_stream_id5 = self.create_request_stream(protocol)
        
        # Test with urn scheme (uniform resource names, no authority)
        violation_headers5 = [
            (b":method", b"GET"),
            (b":path", b"isbn:0451450523"),  # URN path
            (b":scheme", b"urn"),  # Scheme without mandatory authority
            (b":authority", b"urn-resolver.org"),  # FORBIDDEN: :authority with urn scheme
            (b"x-test-case", b"33"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, violation_headers5, end_stream=False)
            self.results.add_step("urn_with_authority_sent", True)
            print(f"✅ Fifth HEADERS frame with urn + :authority sent on stream {request_stream_id5}")
            print(f"   └─ :scheme: 'urn' (no authority component)")
            print(f"   └─ :authority: 'urn-resolver.org' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send fifth HEADERS frame: {e}")
            self.results.add_step("urn_with_authority_sent", False)
            self.results.add_note(f"Fifth HEADERS frame sending failed: {str(e)}")
        
        # Step 8: Send sixth test with empty :authority (still forbidden for non-authority schemes)
        print("📍 Sending sixth request with mailto scheme and empty :authority")
        request_stream_id6 = self.create_request_stream(protocol)
        
        # Test with non-authority scheme and empty :authority (double violation)
        violation_headers6 = [
            (b":method", b"POST"),
            (b":path", b"support@example.com"),
            (b":scheme", b"mailto"),  # Scheme without mandatory authority
            (b":authority", b""),  # FORBIDDEN: Empty :authority (and shouldn't be present at all)
            (b"x-test-case", b"33"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, violation_headers6, end_stream=False)
            self.results.add_step("empty_authority_non_authority_scheme_sent", True)
            print(f"✅ Sixth HEADERS frame with mailto + empty :authority sent on stream {request_stream_id6}")
            print(f"   └─ :scheme: 'mailto' (no authority component)")
            print(f"   └─ :authority: '' (empty and forbidden)")
        except Exception as e:
            print(f"❌ Failed to send sixth HEADERS frame: {e}")
            self.results.add_step("empty_authority_non_authority_scheme_sent", False)
            self.results.add_note(f"Sixth HEADERS frame sending failed: {str(e)}")
        
        # Step 9: Attempt to send DATA frames (if headers were accepted)
        print("📍 Sending DATA frames with request bodies")
        
        try:
            request_body1 = b'To: user@example.com\r\nSubject: Test Email\r\n\r\nThis is a test email via HTTP/3.'
            self.h3_api.send_data_frame(request_stream_id, request_body1, end_stream=True)
            self.results.add_step("request_body_1_sent", True)
            print(f"✅ First DATA frame sent on stream {request_stream_id}")
        except Exception as e:
            print(f"❌ Failed to send first DATA frame: {e}")
            self.results.add_step("request_body_1_sent", False)
        
        try:
            request_body2 = b'{"action": "read_file", "path": "/etc/passwd"}'
            self.h3_api.send_data_frame(request_stream_id2, request_body2, end_stream=True)
            self.results.add_step("request_body_2_sent", True)
            print(f"✅ Second DATA frame sent on stream {request_stream_id2}")
        except Exception as e:
            print(f"❌ Failed to send second DATA frame: {e}")
            self.results.add_step("request_body_2_sent", False)
        
        try:
            request_body3 = b'{"message": "Requesting inline data"}'
            self.h3_api.send_data_frame(request_stream_id3, request_body3, end_stream=True)
            self.results.add_step("request_body_3_sent", True)
            print(f"✅ Third DATA frame sent on stream {request_stream_id3}")
        except Exception as e:
            print(f"❌ Failed to send third DATA frame: {e}")
            self.results.add_step("request_body_3_sent", False)
        
        try:
            request_body4 = b'{"action": "call", "number": "+1-800-555-0123"}'
            self.h3_api.send_data_frame(request_stream_id4, request_body4, end_stream=True)
            self.results.add_step("request_body_4_sent", True)
            print(f"✅ Fourth DATA frame sent on stream {request_stream_id4}")
        except Exception as e:
            print(f"❌ Failed to send fourth DATA frame: {e}")
            self.results.add_step("request_body_4_sent", False)
        
        try:
            request_body5 = b'{"action": "resolve", "urn": "isbn:0451450523"}'
            self.h3_api.send_data_frame(request_stream_id5, request_body5, end_stream=True)
            self.results.add_step("request_body_5_sent", True)
            print(f"✅ Fifth DATA frame sent on stream {request_stream_id5}")
        except Exception as e:
            print(f"❌ Failed to send fifth DATA frame: {e}")
            self.results.add_step("request_body_5_sent", False)
        
        try:
            request_body6 = b'To: support@example.com\r\nSubject: Support Request\r\n\r\nNeed help with service.'
            self.h3_api.send_data_frame(request_stream_id6, request_body6, end_stream=True)
            self.results.add_step("request_body_6_sent", True)
            print(f"✅ Sixth DATA frame sent on stream {request_stream_id6}")
        except Exception as e:
            print(f"❌ Failed to send sixth DATA frame: {e}")
            self.results.add_step("request_body_6_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with :authority for non-authority schemes (protocol violation)")
        self.results.add_note("Non-authority schemes MUST NOT contain :authority pseudo-header")
        self.results.add_note("Tested schemes: mailto, file, data, tel, urn (all non-authority)")
        self.results.add_note("Authority schemes (http/https) require authority; non-authority schemes forbid it")
        self.results.add_note("Scheme-authority consistency is critical for proper URI semantics")


async def main():
    """Main entry point for Test Case 33."""
    test_client = TestCase33Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 