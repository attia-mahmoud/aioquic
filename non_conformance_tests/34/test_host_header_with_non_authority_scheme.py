#!/usr/bin/env python3

"""
Non-Conformance Test Case #34: Host Header with Non-Authority Scheme

Violates HTTP/3 specifications by sending a request with a scheme that 
does not have a mandatory authority component (like 'mailto:') but 
includes a Host header field. If the scheme does not have a mandatory 
authority component and none is provided in the request target, the 
request MUST NOT contain the Host header field.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase34Client(BaseTestClient):
    """Test Case 34: Request with Host header for non-authority schemes."""
    
    def __init__(self):
        super().__init__(
            test_case_id=34,
            test_name="Host header with non-authority scheme",
            violation_description="Non-authority schemes MUST NOT contain Host header field",
            rfc_section="HTTP/3 Scheme-Specific Host Header Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 34."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create request stream
        print("📍 Creating request stream")
        request_stream_id = self.create_request_stream(protocol)
        
        # Step 3: Send HEADERS frame with mailto scheme + Host header - VIOLATION!
        print("📍 Sending HEADERS frame with mailto scheme and Host header")
        print("🚫 PROTOCOL VIOLATION: Non-authority schemes MUST NOT contain Host header!")
        print("🚫 Expected error: Connection termination or header rejection")
        
        # Create headers with mailto scheme (no authority component) but include Host header
        # This violates HTTP/3 specification for scheme-host consistency
        violation_headers = [
            (b":method", b"POST"),
            (b":path", b"user@example.com"),  # mailto path format
            (b":scheme", b"mailto"),  # Scheme without mandatory authority
            (b"host", b"mail-server.com"),  # FORBIDDEN: Host header with non-authority scheme
            (b"x-test-case", b"34"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
            (b"content-type", b"message/rfc822"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, violation_headers, end_stream=False)
            self.results.add_step("mailto_with_host_sent", True)
            print(f"✅ HEADERS frame with mailto + Host sent on stream {request_stream_id}")
            print(f"   └─ Headers: {len(violation_headers)} header fields")
            print(f"   └─ :scheme: 'mailto' (no authority component)")
            print(f"   └─ Host: 'mail-server.com' (forbidden)")
            print(f"   └─ This violates HTTP/3 scheme-host requirements!")
        except Exception as e:
            print(f"❌ Failed to send HEADERS frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("mailto_with_host_sent", True)
            self.results.add_note(f"HEADERS frame sending failed: {str(e)}")
            return
        
        # Step 4: Send another test with file scheme + Host header
        print("📍 Sending second request with file scheme and Host header")
        request_stream_id2 = self.create_request_stream(protocol)
        
        # Test with file scheme (also no authority component)
        violation_headers2 = [
            (b":method", b"GET"),
            (b":path", b"/etc/passwd"),  # file path
            (b":scheme", b"file"),  # Scheme without mandatory authority
            (b"host", b"file-server.local"),  # FORBIDDEN: Host header with file scheme
            (b"x-test-case", b"34"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, violation_headers2, end_stream=False)
            self.results.add_step("file_with_host_sent", True)
            print(f"✅ Second HEADERS frame with file + Host sent on stream {request_stream_id2}")
            print(f"   └─ :scheme: 'file' (no authority component)")
            print(f"   └─ Host: 'file-server.local' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send second HEADERS frame: {e}")
            self.results.add_step("file_with_host_sent", False)
            self.results.add_note(f"Second HEADERS frame sending failed: {str(e)}")
        
        # Step 5: Send third test with data scheme + Host header
        print("📍 Sending third request with data scheme and Host header")
        request_stream_id3 = self.create_request_stream(protocol)
        
        # Test with data scheme (inline data, no authority)
        violation_headers3 = [
            (b":method", b"GET"),
            (b":path", b"text/plain;charset=utf-8,Hello%20World"),  # data URI path
            (b":scheme", b"data"),  # Scheme without mandatory authority
            (b"host", b"data-processor.com"),  # FORBIDDEN: Host header with data scheme
            (b"x-test-case", b"34"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, violation_headers3, end_stream=False)
            self.results.add_step("data_with_host_sent", True)
            print(f"✅ Third HEADERS frame with data + Host sent on stream {request_stream_id3}")
            print(f"   └─ :scheme: 'data' (no authority component)")
            print(f"   └─ Host: 'data-processor.com' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send third HEADERS frame: {e}")
            self.results.add_step("data_with_host_sent", False)
            self.results.add_note(f"Third HEADERS frame sending failed: {str(e)}")
        
        # Step 6: Send fourth test with tel scheme + Host header
        print("📍 Sending fourth request with tel scheme and Host header")
        request_stream_id4 = self.create_request_stream(protocol)
        
        # Test with tel scheme (telephone numbers, no authority)
        violation_headers4 = [
            (b":method", b"GET"),
            (b":path", b"+1-800-555-0123"),  # telephone number path
            (b":scheme", b"tel"),  # Scheme without mandatory authority
            (b"host", b"telecom-gateway.net"),  # FORBIDDEN: Host header with tel scheme
            (b"x-test-case", b"34"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, violation_headers4, end_stream=False)
            self.results.add_step("tel_with_host_sent", True)
            print(f"✅ Fourth HEADERS frame with tel + Host sent on stream {request_stream_id4}")
            print(f"   └─ :scheme: 'tel' (no authority component)")
            print(f"   └─ Host: 'telecom-gateway.net' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send fourth HEADERS frame: {e}")
            self.results.add_step("tel_with_host_sent", False)
            self.results.add_note(f"Fourth HEADERS frame sending failed: {str(e)}")
        
        # Step 7: Send fifth test with urn scheme + Host header
        print("📍 Sending fifth request with urn scheme and Host header")
        request_stream_id5 = self.create_request_stream(protocol)
        
        # Test with urn scheme (uniform resource names, no authority)
        violation_headers5 = [
            (b":method", b"GET"),
            (b":path", b"isbn:0451450523"),  # URN path
            (b":scheme", b"urn"),  # Scheme without mandatory authority
            (b"host", b"urn-resolver.org"),  # FORBIDDEN: Host header with urn scheme
            (b"x-test-case", b"34"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, violation_headers5, end_stream=False)
            self.results.add_step("urn_with_host_sent", True)
            print(f"✅ Fifth HEADERS frame with urn + Host sent on stream {request_stream_id5}")
            print(f"   └─ :scheme: 'urn' (no authority component)")
            print(f"   └─ Host: 'urn-resolver.org' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send fifth HEADERS frame: {e}")
            self.results.add_step("urn_with_host_sent", False)
            self.results.add_note(f"Fifth HEADERS frame sending failed: {str(e)}")
        
        # Step 8: Send sixth test with empty Host header (still forbidden for non-authority schemes)
        print("📍 Sending sixth request with mailto scheme and empty Host header")
        request_stream_id6 = self.create_request_stream(protocol)
        
        # Test with non-authority scheme and empty Host header (double violation)
        violation_headers6 = [
            (b":method", b"POST"),
            (b":path", b"support@example.com"),
            (b":scheme", b"mailto"),  # Scheme without mandatory authority
            (b"host", b""),  # FORBIDDEN: Empty Host header (and shouldn't be present at all)
            (b"x-test-case", b"34"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, violation_headers6, end_stream=False)
            self.results.add_step("empty_host_non_authority_scheme_sent", True)
            print(f"✅ Sixth HEADERS frame with mailto + empty Host sent on stream {request_stream_id6}")
            print(f"   └─ :scheme: 'mailto' (no authority component)")
            print(f"   └─ Host: '' (empty and forbidden)")
        except Exception as e:
            print(f"❌ Failed to send sixth HEADERS frame: {e}")
            self.results.add_step("empty_host_non_authority_scheme_sent", False)
            self.results.add_note(f"Sixth HEADERS frame sending failed: {str(e)}")
        
        # Step 9: Send seventh test with multiple Host headers (triple violation)
        print("📍 Sending seventh request with file scheme and duplicate Host headers")
        request_stream_id7 = self.create_request_stream(protocol)
        
        # Test with non-authority scheme and duplicate Host headers
        violation_headers7 = [
            (b":method", b"GET"),
            (b":path", b"/home/user/document.txt"),
            (b":scheme", b"file"),  # Scheme without mandatory authority
            (b"host", b"fileserver1.local"),  # FORBIDDEN: First Host header
            (b"host", b"fileserver2.local"),  # FORBIDDEN: Second Host header (duplicate)
            (b"x-test-case", b"34"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id7, violation_headers7, end_stream=False)
            self.results.add_step("duplicate_host_non_authority_scheme_sent", True)
            print(f"✅ Seventh HEADERS frame with file + duplicate Host sent on stream {request_stream_id7}")
            print(f"   └─ :scheme: 'file' (no authority component)")
            print(f"   └─ Host: 'fileserver1.local' + 'fileserver2.local' (duplicate and forbidden)")
        except Exception as e:
            print(f"❌ Failed to send seventh HEADERS frame: {e}")
            self.results.add_step("duplicate_host_non_authority_scheme_sent", False)
            self.results.add_note(f"Seventh HEADERS frame sending failed: {str(e)}")
        
        # Step 10: Send eighth test with both Host and :authority (quadruple violation)
        print("📍 Sending eighth request with data scheme, Host header, and :authority")
        request_stream_id8 = self.create_request_stream(protocol)
        
        # Test with non-authority scheme and both Host and :authority headers
        violation_headers8 = [
            (b":method", b"GET"),
            (b":path", b"application/json,{\"test\":true}"),
            (b":scheme", b"data"),  # Scheme without mandatory authority
            (b":authority", b"data-authority.com"),  # FORBIDDEN: :authority with non-authority scheme
            (b"host", b"data-host.com"),  # FORBIDDEN: Host header with non-authority scheme
            (b"x-test-case", b"34"),
            (b"user-agent", b"HTTP3-NonConformance-Test/1.0"),
        ]
        
        try:
            self.h3_api.send_headers_frame(request_stream_id8, violation_headers8, end_stream=False)
            self.results.add_step("both_host_authority_non_authority_scheme_sent", True)
            print(f"✅ Eighth HEADERS frame with data + Host + :authority sent on stream {request_stream_id8}")
            print(f"   └─ :scheme: 'data' (no authority component)")
            print(f"   └─ :authority: 'data-authority.com' (forbidden)")
            print(f"   └─ Host: 'data-host.com' (forbidden)")
        except Exception as e:
            print(f"❌ Failed to send eighth HEADERS frame: {e}")
            self.results.add_step("both_host_authority_non_authority_scheme_sent", False)
            self.results.add_note(f"Eighth HEADERS frame sending failed: {str(e)}")
        
        # Step 11: Attempt to send DATA frames (if headers were accepted)
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
        
        try:
            request_body7 = b'{"file": "/home/user/document.txt", "operation": "read"}'
            self.h3_api.send_data_frame(request_stream_id7, request_body7, end_stream=True)
            self.results.add_step("request_body_7_sent", True)
            print(f"✅ Seventh DATA frame sent on stream {request_stream_id7}")
        except Exception as e:
            print(f"❌ Failed to send seventh DATA frame: {e}")
            self.results.add_step("request_body_7_sent", False)
        
        try:
            request_body8 = b'{"data_type": "json", "inline": true}'
            self.h3_api.send_data_frame(request_stream_id8, request_body8, end_stream=True)
            self.results.add_step("request_body_8_sent", True)
            print(f"✅ Eighth DATA frame sent on stream {request_stream_id8}")
        except Exception as e:
            print(f"❌ Failed to send eighth DATA frame: {e}")
            self.results.add_step("request_body_8_sent", False)
        
        # Add test-specific observations
        self.results.add_note("Requests sent with Host header for non-authority schemes (protocol violation)")
        self.results.add_note("Non-authority schemes MUST NOT contain Host header field")
        self.results.add_note("Tested schemes: mailto, file, data, tel, urn (all non-authority)")
        self.results.add_note("Host header is companion to :authority; both forbidden for non-authority schemes")
        self.results.add_note("Scheme-host consistency is critical for proper HTTP/3 semantics")
        self.results.add_note("Tested variations: normal Host, empty Host, duplicate Host, Host+:authority")


async def main():
    """Main entry point for Test Case 34."""
    test_client = TestCase34Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 