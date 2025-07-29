#!/usr/bin/env python3

"""
Non-Conformance Test Case #39: Push Stream without MAX_PUSH_ID

Tests server behavior when it attempts to initiate push streams without 
the client having sent a MAX_PUSH_ID frame. According to HTTP/3 
specifications, a client MUST treat receipt of a push stream as a 
connection error of type H3_ID_ERROR when no MAX_PUSH_ID frame has been sent.
This test deliberately omits sending MAX_PUSH_ID and observes server behavior.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase39Client(BaseTestClient):
    """Test Case 39: Server push without client sending MAX_PUSH_ID frame."""
    
    def __init__(self):
        super().__init__(
            test_case_id=39,
            test_name="Push stream without MAX_PUSH_ID frame",
            violation_description="Server MUST NOT push when client hasn't sent MAX_PUSH_ID",
            rfc_section="HTTP/3 Server Push Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 39."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Deliberately NOT send MAX_PUSH_ID frame
        print("📍 Deliberately NOT sending MAX_PUSH_ID frame")
        print("🚫 CLIENT BEHAVIOR: No MAX_PUSH_ID sent - server push should be disabled")
        print("🚫 Expected: Server MUST NOT initiate any push streams")
        
        # Note: We explicitly do NOT call any method to send MAX_PUSH_ID
        # This means the server should not attempt any server push
        self.results.add_step("max_push_id_deliberately_omitted", True)
        print("✅ MAX_PUSH_ID frame deliberately omitted")
        print("   └─ Server push should be disabled")
        print("   └─ Any server push attempt would violate HTTP/3 specification")
        
        # Step 3: Create request stream and send requests that typically trigger push
        print("📍 Sending requests that typically trigger server push")
        request_stream_id = self.create_request_stream(protocol)
        
        # Request HTML page that might trigger server push for resources
        html_request_headers = create_common_headers(
            path="/index.html",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.5",
                "accept-encoding": "gzip, deflate, br",
                "x-test-case": "39",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                # Headers that might encourage server push
                "x-request-push-resources": "true",
                "x-expect-resources": "css,js,images"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id, html_request_headers, end_stream=True)
            self.results.add_step("html_request_sent", True)
            print(f"✅ HTML request sent on stream {request_stream_id}")
            print(f"   └─ Path: /index.html")
            print(f"   └─ This might typically trigger server push for CSS/JS/images")
            print(f"   └─ Server MUST NOT push since no MAX_PUSH_ID was sent")
        except Exception as e:
            print(f"❌ Failed to send HTML request: {e}")
            self.results.add_step("html_request_sent", False)
            self.results.add_note(f"HTML request sending failed: {str(e)}")
            return
        
        # Step 4: Send second request for a page with many resources
        print("📍 Sending second request for resource-heavy page")
        request_stream_id2 = self.create_request_stream(protocol)
        
        resource_heavy_headers = create_common_headers(
            path="/dashboard",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "39",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                # Headers suggesting many resources
                "x-page-complexity": "high",
                "x-resource-count": "50+",
                "cache-control": "no-cache"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, resource_heavy_headers, end_stream=True)
            self.results.add_step("resource_heavy_request_sent", True)
            print(f"✅ Resource-heavy request sent on stream {request_stream_id2}")
            print(f"   └─ Path: /dashboard")
            print(f"   └─ Typically has many sub-resources")
        except Exception as e:
            print(f"❌ Failed to send resource-heavy request: {e}")
            self.results.add_step("resource_heavy_request_sent", False)
        
        # Step 5: Send third request with explicit push hints
        print("📍 Sending third request with explicit push hints")
        request_stream_id3 = self.create_request_stream(protocol)
        
        push_hint_headers = create_common_headers(
            path="/app",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "39",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                # Headers that might hint at wanting push
                "x-preferred-push": "css,js,fonts",
                "x-push-policy": "aggressive",
                "priority": "u=1"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, push_hint_headers, end_stream=True)
            self.results.add_step("push_hint_request_sent", True)
            print(f"✅ Push hint request sent on stream {request_stream_id3}")
            print(f"   └─ Path: /app")
            print(f"   └─ Contains headers that might encourage push")
        except Exception as e:
            print(f"❌ Failed to send push hint request: {e}")
            self.results.add_step("push_hint_request_sent", False)
        
        # Step 6: Send fourth request simulating SPA (Single Page Application)
        print("📍 Sending fourth request simulating SPA")
        request_stream_id4 = self.create_request_stream(protocol)
        
        spa_headers = create_common_headers(
            path="/spa",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "39",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                # SPA-specific headers
                "x-app-type": "spa",
                "x-preload-modules": "true",
                "x-bundle-splitting": "enabled"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, spa_headers, end_stream=True)
            self.results.add_step("spa_request_sent", True)
            print(f"✅ SPA request sent on stream {request_stream_id4}")
            print(f"   └─ Path: /spa")
            print(f"   └─ SPAs often benefit from aggressive server push")
        except Exception as e:
            print(f"❌ Failed to send SPA request: {e}")
            self.results.add_step("spa_request_sent", False)
        
        # Step 7: Send fifth request with Link preload headers
        print("📍 Sending fifth request with Link preload headers")
        request_stream_id5 = self.create_request_stream(protocol)
        
        preload_headers = create_common_headers(
            path="/preload-test",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "39",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                # Headers suggesting preload relationships
                "x-preload-css": "/styles/main.css,/styles/theme.css",
                "x-preload-js": "/scripts/app.js,/scripts/vendor.js",
                "x-preload-fonts": "/fonts/main.woff2"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, preload_headers, end_stream=True)
            self.results.add_step("preload_request_sent", True)
            print(f"✅ Preload request sent on stream {request_stream_id5}")
            print(f"   └─ Path: /preload-test")
            print(f"   └─ Contains explicit preload hints")
        except Exception as e:
            print(f"❌ Failed to send preload request: {e}")
            self.results.add_step("preload_request_sent", False)
        
        # Step 8: Send sixth request with cache optimization headers
        print("📍 Sending sixth request with cache optimization headers")
        request_stream_id6 = self.create_request_stream(protocol)
        
        cache_opt_headers = create_common_headers(
            path="/optimized",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "39",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                # Cache optimization headers
                "cache-control": "max-age=0",
                "if-none-match": "*",
                "x-cache-strategy": "push-then-cache"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, cache_opt_headers, end_stream=True)
            self.results.add_step("cache_opt_request_sent", True)
            print(f"✅ Cache optimization request sent on stream {request_stream_id6}")
            print(f"   └─ Path: /optimized")
            print(f"   └─ Headers suggest cache optimization via push")
        except Exception as e:
            print(f"❌ Failed to send cache optimization request: {e}")
            self.results.add_step("cache_opt_request_sent", False)
        
        # Step 9: Wait and observe for any push stream attempts
        print("📍 Observing server behavior for push stream attempts")
        print("⏱️  Waiting for potential server response and push attempts...")
        
        # Give some time for the server to process requests and potentially attempt push
        await asyncio.sleep(2.0)
        
        self.results.add_step("observation_period_completed", True)
        print("✅ Observation period completed")
        print("   └─ Any server push attempts during this period would be violations")
        print("   └─ Server should have processed requests without pushing resources")
        
        # Step 10: Attempt one more request to confirm connection state
        print("📍 Sending final request to confirm connection state")
        request_stream_id7 = self.create_request_stream(protocol)
        
        final_headers = create_common_headers(
            path="/status",
            method="GET",
            **{
                "x-test-case": "39",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "x-final-check": "true"
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id7, final_headers, end_stream=True)
            self.results.add_step("final_request_sent", True)
            print(f"✅ Final request sent on stream {request_stream_id7}")
            print(f"   └─ Connection should still be active")
            print(f"   └─ No push streams should have been initiated")
        except Exception as e:
            print(f"❌ Failed to send final request: {e}")
            self.results.add_step("final_request_sent", False)
            self.results.add_note(f"Final request failed - possible connection error: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note("Client deliberately did NOT send MAX_PUSH_ID frame")
        self.results.add_note("Multiple requests sent that typically trigger server push")
        self.results.add_note("Server MUST NOT initiate push streams without MAX_PUSH_ID")
        self.results.add_note("Any push stream attempts would violate HTTP/3 specification")
        self.results.add_note("Expected behavior: Server processes requests normally, no push")
        self.results.add_note("Violation check: Monitor for H3_ID_ERROR if server attempts push")
        self.results.add_note("Test validates server compliance with MAX_PUSH_ID requirement")


async def main():
    """Main entry point for Test Case 39."""
    test_client = TestCase39Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 