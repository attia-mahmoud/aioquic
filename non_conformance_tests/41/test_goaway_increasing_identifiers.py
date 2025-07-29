#!/usr/bin/env python3

"""
Non-Conformance Test Case #41: GOAWAY Frames with Increasing Identifiers

Violates HTTP/3 specifications by sending multiple GOAWAY frames where 
the identifier in the second frame is greater than the identifier in the 
first frame. According to HTTP/3 specifications, a client MAY send multiple 
GOAWAY frames indicating different identifiers, but the identifier in each 
frame MUST NOT be greater than the identifier in any previous frame, since 
clients might already have retried unprocessed requests on another HTTP connection.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils import BaseTestClient, create_common_headers


class TestCase41Client(BaseTestClient):
    """Test Case 41: Multiple GOAWAY frames with increasing identifiers."""
    
    def __init__(self):
        super().__init__(
            test_case_id=41,
            test_name="GOAWAY frames with increasing identifiers",
            violation_description="GOAWAY frame identifiers MUST NOT increase across multiple frames",
            rfc_section="HTTP/3 GOAWAY Frame Requirements"
        )
    
    async def _execute_test_logic(self, protocol):
        """Execute the specific test logic for Test Case 41."""
        
        # Step 1: Set up conformant HTTP/3 connection
        await self.setup_conformant_connection()
        
        # Step 2: Create and send some initial requests to establish stream IDs
        print("📍 Creating initial requests to establish stream IDs")
        
        request_streams = []
        for i in range(5):
            stream_id = self.create_request_stream(protocol)
            request_streams.append(stream_id)
            
            headers = create_common_headers(
                path=f"/request{i+1}.html",
                method="GET",
                **{
                    "x-test-case": "41",
                    "user-agent": "HTTP3-NonConformance-Test/1.0",
                    "x-request-number": str(i+1)
                }
            )
            
            try:
                self.h3_api.send_headers_frame(stream_id, headers, end_stream=True)
                print(f"✅ Request {i+1} sent on stream {stream_id}")
            except Exception as e:
                print(f"❌ Failed to send request {i+1}: {e}")
        
        self.results.add_step("initial_requests_sent", True)
        print(f"✅ Created {len(request_streams)} initial request streams")
        print(f"   └─ Stream IDs: {request_streams}")
        
        # Step 3: Send first GOAWAY frame with a lower stream ID
        first_goaway_id = request_streams[1]  # Use second stream ID (lower value)
        control_stream_id = self.h3_api.get_control_stream_id()
        
        print(f"📍 Sending first GOAWAY frame with ID = {first_goaway_id}")
        print(f"🔒 FIRST GOAWAY: Stream ID {first_goaway_id}")
        
        if control_stream_id is not None:
            try:
                self.h3_api.send_goaway_frame(control_stream_id, first_goaway_id)
                self.results.add_step("first_goaway_sent", True)
                print(f"✅ First GOAWAY frame sent with stream ID = {first_goaway_id}")
                print(f"   └─ This indicates graceful shutdown starting from stream {first_goaway_id}")
                print(f"   └─ Streams {first_goaway_id} and below should not process new requests")
            except Exception as e:
                print(f"❌ Failed to send first GOAWAY frame: {e}")
                self.results.add_step("first_goaway_sent", False)
                self.results.add_note(f"First GOAWAY sending failed: {str(e)}")
                return
        else:
            print(f"❌ No control stream available to send GOAWAY frames")
            self.results.add_step("first_goaway_sent", False)
            self.results.add_note("No control stream available for GOAWAY")
            return
        
        # Step 4: Wait briefly to simulate processing time
        print("📍 Brief pause to simulate processing...")
        await asyncio.sleep(1.0)
        
        # Step 5: Send second GOAWAY frame with HIGHER stream ID - VIOLATION!
        second_goaway_id = request_streams[3]  # Use fourth stream ID (higher value)
        
        print(f"📍 Sending second GOAWAY frame with ID = {second_goaway_id}")
        print(f"🚫 PROTOCOL VIOLATION: Second GOAWAY ID > First GOAWAY ID!")
        print(f"🚫 First GOAWAY: {first_goaway_id}, Second GOAWAY: {second_goaway_id}")
        print(f"🚫 Expected error: Connection termination or protocol error")
        
        try:
            self.h3_api.send_goaway_frame(control_stream_id, second_goaway_id)
            self.results.add_step("second_goaway_sent", True)
            print(f"✅ Second GOAWAY frame sent with stream ID = {second_goaway_id}")
            print(f"   └─ This violates HTTP/3 GOAWAY identifier requirements!")
            print(f"   └─ Stream ID {second_goaway_id} > {first_goaway_id} (previous GOAWAY)")
            print(f"   └─ This could confuse clients about which streams to retry")
        except Exception as e:
            print(f"❌ Failed to send second GOAWAY frame: {e}")
            print("   └─ This may indicate the violation was caught early")
            self.results.add_step("second_goaway_sent", True)
            self.results.add_note(f"Second GOAWAY sending failed: {str(e)}")
        
        # Step 6: Send third GOAWAY frame with even higher ID (escalating violation)
        print("📍 Sending third GOAWAY frame with even higher ID")
        
        # Create a new stream to get an even higher ID
        third_stream_id = self.create_request_stream(protocol)
        third_goaway_id = third_stream_id
        
        print(f"🚫 ESCALATING VIOLATION: Third GOAWAY ID = {third_goaway_id}")
        print(f"🚫 Sequence: {first_goaway_id} → {second_goaway_id} → {third_goaway_id}")
        
        try:
            self.h3_api.send_goaway_frame(control_stream_id, third_goaway_id)
            self.results.add_step("third_goaway_sent", True)
            print(f"✅ Third GOAWAY frame sent with stream ID = {third_goaway_id}")
            print(f"   └─ This further violates GOAWAY identifier ordering")
        except Exception as e:
            print(f"❌ Failed to send third GOAWAY frame: {e}")
            self.results.add_step("third_goaway_sent", False)
            self.results.add_note(f"Third GOAWAY sending failed: {str(e)}")
        
        # Step 7: Send fourth GOAWAY with correct decreasing ID (conformant)
        print("📍 Sending fourth GOAWAY frame with correctly decreasing ID")
        
        fourth_goaway_id = request_streams[0]  # Use first stream ID (lowest value)
        
        print(f"✅ CONFORMANT GOAWAY: Fourth GOAWAY ID = {fourth_goaway_id}")
        print(f"✅ This correctly decreases: {third_goaway_id} → {fourth_goaway_id}")
        
        try:
            self.h3_api.send_goaway_frame(control_stream_id, fourth_goaway_id)
            self.results.add_step("fourth_goaway_sent", True)
            print(f"✅ Fourth GOAWAY frame sent with stream ID = {fourth_goaway_id}")
            print(f"   └─ This follows correct GOAWAY identifier ordering")
            print(f"   └─ Shows what conformant behavior should look like")
        except Exception as e:
            print(f"❌ Failed to send fourth GOAWAY frame: {e}")
            self.results.add_step("fourth_goaway_sent", False)
            self.results.add_note(f"Fourth GOAWAY sending failed: {str(e)}")
        
        # Step 8: Attempt to send more requests after GOAWAY frames
        print("📍 Attempting to send requests after GOAWAY frames")
        
        for i in range(3):
            stream_id = self.create_request_stream(protocol)
            headers = create_common_headers(
                path=f"/post-goaway{i+1}.html",
                method="GET",
                **{
                    "x-test-case": "41",
                    "user-agent": "HTTP3-NonConformance-Test/1.0",
                    "x-post-goaway": "true",
                    "x-request-number": str(i+1)
                }
            )
            
            try:
                self.h3_api.send_headers_frame(stream_id, headers, end_stream=True)
                self.results.add_step(f"post_goaway_request_{i+1}_sent", True)
                print(f"✅ Post-GOAWAY request {i+1} sent on stream {stream_id}")
            except Exception as e:
                print(f"❌ Failed to send post-GOAWAY request {i+1}: {e}")
                self.results.add_step(f"post_goaway_request_{i+1}_sent", False)
        
        # Step 9: Send fifth GOAWAY with extreme violation (much higher ID)
        print("📍 Sending fifth GOAWAY frame with extreme ID violation")
        
        extreme_goaway_id = max(request_streams) + 1000  # Extremely high ID
        
        print(f"🚫 EXTREME VIOLATION: Fifth GOAWAY ID = {extreme_goaway_id}")
        print(f"🚫 This is much higher than any previous ID")
        
        try:
            self.h3_api.send_goaway_frame(control_stream_id, extreme_goaway_id)
            self.results.add_step("extreme_goaway_sent", True)
            print(f"✅ Extreme GOAWAY frame sent with stream ID = {extreme_goaway_id}")
            print(f"   └─ This represents a severe GOAWAY ordering violation")
        except Exception as e:
            print(f"❌ Failed to send extreme GOAWAY frame: {e}")
            self.results.add_step("extreme_goaway_sent", False)
            self.results.add_note(f"Extreme GOAWAY sending failed: {str(e)}")
        
        # Step 10: Wait and observe connection behavior
        print("📍 Observing connection behavior after GOAWAY violations")
        await asyncio.sleep(2.0)
        
        # Step 11: Attempt final request to test connection state
        print("📍 Sending final request to test connection state")
        
        try:
            final_stream_id = self.create_request_stream(protocol)
            final_headers = create_common_headers(
                path="/final-status",
                method="GET",
                **{
                    "x-test-case": "41",
                    "user-agent": "HTTP3-NonConformance-Test/1.0",
                    "x-final-check": "true"
                }
            )
            
            self.h3_api.send_headers_frame(final_stream_id, final_headers, end_stream=True)
            self.results.add_step("final_request_sent", True)
            print(f"✅ Final request sent on stream {final_stream_id}")
            print(f"   └─ Connection may still be active despite GOAWAY violations")
        except Exception as e:
            print(f"❌ Failed to send final request: {e}")
            self.results.add_step("final_request_sent", False)
            self.results.add_note(f"Final request failed - possible connection termination: {str(e)}")
        
        # Add test-specific observations
        self.results.add_note(f"Multiple GOAWAY frames sent with increasing identifiers (protocol violation)")
        self.results.add_note(f"GOAWAY sequence: {first_goaway_id} → {second_goaway_id} → {third_goaway_id} → {fourth_goaway_id} → {extreme_goaway_id}")
        self.results.add_note(f"Violations: Second, third, and extreme GOAWAY IDs were higher than previous")
        self.results.add_note(f"Conformant: Fourth GOAWAY ID correctly decreased")
        self.results.add_note("GOAWAY identifiers MUST NOT increase to avoid client retry confusion")
        self.results.add_note("Increasing GOAWAY IDs can cause clients to retry already-processed requests")
        self.results.add_note("Test validates server handling of malformed GOAWAY sequences")


async def main():
    """Main entry point for Test Case 41."""
    test_client = TestCase41Client()
    await BaseTestClient.main(test_client)


if __name__ == "__main__":
    asyncio.run(main()) 