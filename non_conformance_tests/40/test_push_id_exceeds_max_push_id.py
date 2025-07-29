#!/usr/bin/env python3

"""
Non-Conformance Test Case #40: Push ID Exceeds MAX_PUSH_ID

Tests server behavior when it attempts to use push IDs that exceed the 
client's declared MAX_PUSH_ID limit. According to HTTP/3 specifications, 
a client MUST treat receipt of a push stream as a connection error of type 
H3_ID_ERROR when the stream references a push ID that is greater than the 
maximum push ID. This test sets MAX_PUSH_ID to 3 and observes if the server 
attempts to push with IDs greater than 3.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase40Client(BaseTestClient):
    """Test Case 40: Server push with push ID exceeding MAX_PUSH_ID limit."""
    
    def __init__(self):
        super().__init__(
            test_case_id=40,
            test_name="Push ID exceeds MAX_PUSH_ID limit",
            violation_description="Server MUST NOT use push IDs greater than client's MAX_PUSH_ID",
            rfc_section="HTTP/3 Server Push ID Management"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 40."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Send MAX_PUSH_ID frame with limited value
        max_push_id_limit = 3
        print(f"📍 Sending MAX_PUSH_ID frame with limit = {max_push_id_limit}")
        print(f"🔒 CLIENT LIMIT: Server can only use push IDs 0, 1, 2, 3")
        print(f"🚫 Expected: Server MUST NOT use push IDs 4, 5, 6, etc.")
        
        try:
            # Send MAX_PUSH_ID frame to enable server push with a specific limit
            # This allows the server to use push IDs 0, 1, 2, 3 only
            control_stream_id = self.h3_api.get_control_stream_id()
            if control_stream_id is not None:
                self.h3_api.send_max_push_id_frame(control_stream_id, max_push_id_limit)
                self.results.add_step("max_push_id_sent", True)
                print(f"✅ MAX_PUSH_ID frame sent with limit = {max_push_id_limit}")
                print(f"   └─ Server can use push IDs: 0, 1, 2, 3")
                print(f"   └─ Push IDs 4+ would violate the limit")
            else:
                print(f"❌ No control stream available to send MAX_PUSH_ID frame")
                self.results.add_step("max_push_id_sent", False)
                self.results.add_note("No control stream available for MAX_PUSH_ID")
        except Exception as e:
            print(f"❌ Failed to send MAX_PUSH_ID frame: {e}")
            print("   └─ Will proceed with requests anyway to test server behavior")
            self.results.add_step("max_push_id_sent", False)
            self.results.add_note(f"MAX_PUSH_ID sending failed: {str(e)}")
        
        # Step 3: Send multiple requests to encourage server push beyond limit
        print("📍 Sending multiple requests to encourage server push")
        
        # Request 1: Main HTML page
        request_stream_id1 = self.create_request_stream(protocol)
        html_headers = create_common_headers(
            path="/main.html",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "40",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "x-push-resources": "css,js,images,fonts",
                "x-max-push-id": str(max_push_id_limit)
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id1, html_headers, end_stream=True)
            self.results.add_step("request_1_sent", True)
            print(f"✅ Request 1 sent on stream {request_stream_id1} (/main.html)")
            print(f"   └─ This might trigger push for: CSS, JS, images, fonts")
        except Exception as e:
            print(f"❌ Failed to send request 1: {e}")
            self.results.add_step("request_1_sent", False)
        
        # Request 2: Dashboard with many resources
        request_stream_id2 = self.create_request_stream(protocol)
        dashboard_headers = create_common_headers(
            path="/dashboard.html",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "40",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "x-resource-heavy": "true",
                "x-expect-push-count": "10+",
                "x-max-push-id": str(max_push_id_limit)
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id2, dashboard_headers, end_stream=True)
            self.results.add_step("request_2_sent", True)
            print(f"✅ Request 2 sent on stream {request_stream_id2} (/dashboard.html)")
            print(f"   └─ This might trigger push for many resources (10+ expected)")
        except Exception as e:
            print(f"❌ Failed to send request 2: {e}")
            self.results.add_step("request_2_sent", False)
        
        # Request 3: Application with modules
        request_stream_id3 = self.create_request_stream(protocol)
        app_headers = create_common_headers(
            path="/app.html",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "40",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "x-modules": "core,auth,ui,api,utils",
                "x-aggressive-push": "true",
                "x-max-push-id": str(max_push_id_limit)
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id3, app_headers, end_stream=True)
            self.results.add_step("request_3_sent", True)
            print(f"✅ Request 3 sent on stream {request_stream_id3} (/app.html)")
            print(f"   └─ This might trigger push for multiple modules")
        except Exception as e:
            print(f"❌ Failed to send request 3: {e}")
            self.results.add_step("request_3_sent", False)
        
        # Request 4: Media-rich page
        request_stream_id4 = self.create_request_stream(protocol)
        media_headers = create_common_headers(
            path="/gallery.html",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "40",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "x-media-count": "20",
                "x-thumbnail-push": "enabled",
                "x-preload-images": "true",
                "x-max-push-id": str(max_push_id_limit)
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id4, media_headers, end_stream=True)
            self.results.add_step("request_4_sent", True)
            print(f"✅ Request 4 sent on stream {request_stream_id4} (/gallery.html)")
            print(f"   └─ This might trigger push for 20+ media resources")
        except Exception as e:
            print(f"❌ Failed to send request 4: {e}")
            self.results.add_step("request_4_sent", False)
        
        # Request 5: E-commerce product page
        request_stream_id5 = self.create_request_stream(protocol)
        product_headers = create_common_headers(
            path="/product.html",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "40",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "x-product-images": "15",
                "x-related-products": "8",
                "x-push-strategy": "all-resources",
                "x-max-push-id": str(max_push_id_limit)
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id5, product_headers, end_stream=True)
            self.results.add_step("request_5_sent", True)
            print(f"✅ Request 5 sent on stream {request_stream_id5} (/product.html)")
            print(f"   └─ This might trigger push for product and related resources")
        except Exception as e:
            print(f"❌ Failed to send request 5: {e}")
            self.results.add_step("request_5_sent", False)
        
        # Request 6: Documentation with code examples
        request_stream_id6 = self.create_request_stream(protocol)
        docs_headers = create_common_headers(
            path="/docs.html",
            method="GET",
            **{
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "x-test-case": "40",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "x-code-samples": "25",
                "x-syntax-highlighting": "true",
                "x-push-all-assets": "true",
                "x-max-push-id": str(max_push_id_limit)
            }
        )
        
        try:
            self.h3_api.send_headers_frame(request_stream_id6, docs_headers, end_stream=True)
            self.results.add_step("request_6_sent", True)
            print(f"✅ Request 6 sent on stream {request_stream_id6} (/docs.html)")
            print(f"   └─ This might trigger push for documentation assets")
        except Exception as e:
            print(f"❌ Failed to send request 6: {e}")
            self.results.add_step("request_6_sent", False)
        
        # Step 4: Send additional requests to maximize push trigger attempts
        print("📍 Sending additional requests to maximize push attempts")
        
        for i in range(7, 12):  # Requests 7-11
            request_stream_id = self.create_request_stream(protocol)
            extra_headers = create_common_headers(
                path=f"/page{i}.html",
                method="GET",
                **{
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "x-test-case": "40",
                    "user-agent": "HTTP3-NonConformance-Test/1.0",
                    "x-push-encouragement": f"request-{i}",
                    "x-resource-intensive": "true",
                    "x-max-push-id": str(max_push_id_limit)
                }
            )
            
            try:
                self.h3_api.send_headers_frame(request_stream_id, extra_headers, end_stream=True)
                self.results.add_step(f"request_{i}_sent", True)
                print(f"✅ Request {i} sent on stream {request_stream_id} (/page{i}.html)")
            except Exception as e:
                print(f"❌ Failed to send request {i}: {e}")
                self.results.add_step(f"request_{i}_sent", False)
        
        # Step 5: Observation period
        print("📍 Observing server push behavior")
        print(f"⏱️  Monitoring for push IDs > {max_push_id_limit} (violation)")
        print(f"✅  Valid push IDs: 0, 1, 2, 3")
        print(f"🚫  Invalid push IDs: 4, 5, 6, 7, 8, ...")
        
        # Extended observation period to allow server to process all requests
        await asyncio.sleep(3.0)
        
        self.results.add_step("observation_period_completed", True)
        print("✅ Observation period completed")
        print("   └─ Any push attempts with ID > 3 would be violations")
        print("   └─ Server should have respected MAX_PUSH_ID limit")
        
        # Step 6: Final status check
        print("📍 Sending final status request")
        final_stream_id = self.create_request_stream(protocol)
        status_headers = create_common_headers(
            path="/status",
            method="GET",
            **{
                "x-test-case": "40",
                "user-agent": "HTTP3-NonConformance-Test/1.0",
                "x-final-check": "true",
                "x-push-id-limit": str(max_push_id_limit)
            }
        )
        
        try:
            self.h3_api.send_headers_frame(final_stream_id, status_headers, end_stream=True)
            self.results.add_step("final_status_sent", True)
            print(f"✅ Final status request sent on stream {final_stream_id}")
            print(f"   └─ Connection should still be active")
            print(f"   └─ No H3_ID_ERROR should have occurred")
        except Exception as e:
            print(f"❌ Failed to send final status request: {e}")
            self.results.add_step("final_status_sent", False)
            self.results.add_note(f"Final request failed - possible H3_ID_ERROR: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note(f"Client sent MAX_PUSH_ID = {max_push_id_limit} (allows push IDs 0-3)")
        self.results.add_note("Multiple resource-intensive requests sent to trigger push")
        self.results.add_note("Server MUST NOT use push IDs > 3")
        self.results.add_note("Push ID violations should trigger H3_ID_ERROR")
        self.results.add_note("Expected: Server respects push ID limit or doesn't push")
        self.results.add_note("Violation: Server uses push IDs 4, 5, 6, etc.")
        self.results.add_note("Test validates server compliance with MAX_PUSH_ID limits")
    



async def main():
    """Main entry point for Test Case 40."""
    test_client = TestCase40Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 