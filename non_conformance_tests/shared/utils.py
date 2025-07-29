#!/usr/bin/env python3

"""
Shared Utilities for HTTP/3 Non-Conformance Tests

This module provides common functions and utilities used across multiple
non-conformance test cases.
"""

import argparse
import asyncio
import logging
import ssl
import sys
import os
import time
from typing import Dict, List, Optional, Tuple, Any

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.custom_api import H3CustomAPI
from aioquic.quic.configuration import QuicConfiguration


class TestResult:
    """Container for test execution results."""
    
    def __init__(self, test_case_id: int, test_name: str):
        self.test_case_id = test_case_id
        self.test_name = test_name
        self.steps: Dict[str, bool] = {}
        self.error_code: Optional[int] = None
        self.error_reason: Optional[str] = None
        self.connection_terminated = False
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.notes: List[str] = []
    
    def add_step(self, step_name: str, success: bool):
        """Record a test step result."""
        self.steps[step_name] = success
    
    def add_note(self, note: str):
        """Add an observation note."""
        self.notes.append(note)
    
    def set_error(self, error_code: int, error_reason: str):
        """Record connection error details."""
        self.error_code = error_code
        self.error_reason = error_reason
        self.connection_terminated = True


class NonConformanceProtocol(QuicConnectionProtocol):
    """Enhanced protocol with event logging for non-conformance tests."""
    
    def __init__(self, *args, test_results: TestResult, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_results = test_results
    
    def quic_event_received(self, event):
        """Handle QUIC events with minimal logging."""
        from aioquic.quic import events
        
        if isinstance(event, events.ConnectionTerminated):
            error_name = parse_error_code(event.error_code)
            self.test_results.set_error(event.error_code, event.reason_phrase)
            self.test_results.add_note(f"Connection terminated: {error_name} - {event.reason_phrase}")
            
        elif isinstance(event, events.StreamReset):
            self.test_results.add_note(f"Stream {event.stream_id} reset (code: {event.error_code})")


class BaseTestClient:
    """Base class for non-conformance test clients with common functionality."""
    
    def __init__(self, test_case_id: int, test_name: str, violation_description: str, rfc_section: str):
        self.test_case_id = test_case_id
        self.test_name = test_name
        self.violation_description = violation_description
        self.rfc_section = rfc_section
        self.h3_api: Optional[H3CustomAPI] = None
        self.results = TestResult(test_case_id, test_name)
        
        # Connection state
        self.control_stream_id: Optional[int] = None
        self.encoder_stream_id: Optional[int] = None
        self.decoder_stream_id: Optional[int] = None
        self.request_stream_id: Optional[int] = None
    
    async def run_test(self, host: str = "localhost", port: int = 4433, verbose: bool = False):
        """Main test execution method - override in subclasses."""
        setup_logging(verbose)
        self.results.start_time = time.time()
        
        self._print_test_header(host, port)
        
        try:
            async with self._connect_to_target(host, port) as protocol:
                self.h3_api = H3CustomAPI(protocol._quic)
                self.results.add_step("connection_established", True)
                
                # Execute the test-specific logic
                await self._execute_test_logic(protocol)
                
                # Wait and observe
                await self._observe_behavior()
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            self.results.add_note(f"Test exception: {str(e)}")
        
        self.results.end_time = time.time()
        self._print_test_results()
    
    async def _execute_test_logic(self, protocol):
        """Override this method in subclasses to implement test-specific logic."""
        raise NotImplementedError("Subclasses must implement _execute_test_logic")
    
    def _connect_to_target(self, host: str, port: int):
        """Establish QUIC connection to target."""
        configuration = QuicConfiguration(
            is_client=True,
            alpn_protocols=["h3"],
            verify_mode=ssl.CERT_NONE,
        )
        
        return connect(
            host, port,
            configuration=configuration,
            create_protocol=lambda *args, **kwargs: NonConformanceProtocol(
                *args, **kwargs, test_results=self.results
            ),
        )
    
    async def setup_conformant_connection(self):
        """Set up conformant HTTP/3 connection (control stream + SETTINGS + QPACK)."""
        print("📍 Setting up conformant HTTP/3 connection")
        
        # Create control stream and send SETTINGS
        self.control_stream_id = self.h3_api.create_control_stream()
        self.h3_api.send_settings_frame(self.control_stream_id)
        self.results.add_step("control_stream_created", True)
        
        # Create QPACK streams
        self.encoder_stream_id = self.h3_api.create_encoder_stream()
        self.decoder_stream_id = self.h3_api.create_decoder_stream()
        self.results.add_step("qpack_streams_created", True)
        
        print(f"✅ HTTP/3 connection established (control: {self.control_stream_id})")
    
    def create_request_stream(self, protocol):
        """Create a new request stream."""
        self.request_stream_id = protocol._quic.get_next_available_stream_id()
        self.results.add_step("request_stream_created", True)
        return self.request_stream_id
    
    async def _observe_behavior(self, duration: float = 3.0):
        """Wait and observe server behavior."""
        print(f"\n📍 Observing server behavior ({duration}s)")
        await asyncio.sleep(duration)
    
    def _print_test_header(self, host: str, port: int):
        """Print standardized test header."""
        print("=" * 70)
        print(f"🧪 NON-CONFORMANCE TEST CASE #{self.test_case_id}")
        print("=" * 70)
        print(f"📋 Test: {self.test_name}")
        print(f"🚫 Violation: {self.violation_description}")
        print(f"📚 RFC Section: {self.rfc_section}")
        print(f"🎯 Target: {host}:{port}")
        print("=" * 70)
    
    def _print_test_results(self):
        """Print standardized test results."""
        print("\n" + "=" * 70)
        print(f"📊 TEST CASE #{self.test_case_id} RESULTS")
        print("=" * 70)
        
        # Test steps summary
        print("🧪 Test Execution:")
        for step_name, success in self.results.steps.items():
            status = "✅ PASS" if success else "❌ FAIL"
            formatted_name = step_name.replace("_", " ").title()
            print(f"   {status} {formatted_name}")
        
        # Connection termination info
        if self.results.connection_terminated:
            error_name = parse_error_code(self.results.error_code)
            print(f"\n🔌 Connection Terminated: {error_name}")
            if self.results.error_reason:
                print(f"   Reason: {self.results.error_reason}")
        
        # Key observations
        if self.results.notes:
            print("\n📝 Key Observations:")
            for note in self.results.notes:
                print(f"   • {note}")
        
        # Summary stats
        passed = sum(1 for success in self.results.steps.values() if success)
        total = len(self.results.steps)
        duration = self.results.end_time - self.results.start_time if self.results.start_time else 0
        print(f"\n📊 Summary: {passed}/{total} steps passed in {duration:.2f}s")
        print("=" * 70)
    
    @classmethod
    def create_argument_parser(cls, description: str) -> argparse.ArgumentParser:
        """Create standardized argument parser for test cases."""
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--host", default="localhost", help="Target hostname (default: localhost)")
        parser.add_argument("--port", type=int, default=4433, help="Target port (default: 4433)")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
        return parser
    
    @classmethod
    async def main(cls, test_instance):
        """Main entry point for test cases."""
        parser = cls.create_argument_parser(f"Non-Conformance Test Case #{test_instance.test_case_id}")
        args = parser.parse_args()
        
        try:
            await test_instance.run_test(args.host, args.port, args.verbose)
        except KeyboardInterrupt:
            print("\n🛑 Test interrupted by user")
        except Exception as e:
            print(f"\n💥 Test crashed: {e}")


def setup_logging(verbose: bool = False):
    """Configure minimal logging for non-conformance tests."""
    # Reduce logging verbosity significantly
    if verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        force=True
    )
    
    # Silence noisy loggers
    logging.getLogger("quic").setLevel(logging.ERROR)
    logging.getLogger("http3.custom_api").setLevel(logging.ERROR)


def create_common_headers(host: str = "test-server", path: str = "/", method: str = "GET", **extra) -> List[Tuple[bytes, bytes]]:
    """Create standard HTTP/3 headers for testing."""
    headers = [
        (b":method", method.encode()),
        (b":path", path.encode()),
        (b":scheme", b"https"),
        (b":authority", host.encode()),
    ]
    
    # Add extra headers
    for key, value in extra.items():
        headers.append((key.encode() if isinstance(key, str) else key, 
                       value.encode() if isinstance(value, str) else value))
    
    return headers


def parse_error_code(error_code: int) -> str:
    """Parse HTTP/3 error codes into human-readable descriptions."""
    error_codes = {
        0x100: "H3_NO_ERROR",
        0x101: "H3_GENERAL_PROTOCOL_ERROR", 
        0x102: "H3_INTERNAL_ERROR",
        0x103: "H3_STREAM_CREATION_ERROR",
        0x104: "H3_CLOSED_CRITICAL_STREAM",
        0x105: "H3_FRAME_UNEXPECTED", 
        0x106: "H3_FRAME_ERROR",
        0x107: "H3_EXCESSIVE_LOAD",
        0x108: "H3_ID_ERROR",
        0x109: "H3_SETTINGS_ERROR",
        0x10A: "H3_MISSING_SETTINGS",
        0x10B: "H3_REQUEST_REJECTED",
        0x10C: "H3_REQUEST_CANCELLED",
        0x10D: "H3_REQUEST_INCOMPLETE",
        0x10E: "H3_MESSAGE_ERROR",
        0x10F: "H3_CONNECT_ERROR",
        0x110: "H3_VERSION_FALLBACK",
        0x200: "QPACK_DECOMPRESSION_FAILED",
        0x201: "QPACK_ENCODER_STREAM_ERROR",
        0x202: "QPACK_DECODER_STREAM_ERROR",
    }
    
    return error_codes.get(error_code, f"UNKNOWN_0x{error_code:x}")


# Export commonly used classes and functions
__all__ = [
    'TestResult',
    'BaseTestClient', 
    'NonConformanceProtocol',
    'setup_logging',
    'create_common_headers',
    'parse_error_code',
] 