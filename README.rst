HTTP/3 Non-Conformance Testing Framework
========================================

A comprehensive testing framework for HTTP/3 protocol compliance and non-conformance scenarios.

Overview
--------

This framework provides systematic tests for HTTP/3 protocol violations to validate server implementations' error handling and compliance checking. Each test case targets specific protocol violations and expects appropriate error responses.

Quick Start
-----------

1. Start a test server::

    python3 examples/h3_test_server.py

2. Run a non-conformance test::

    python3 non_conformance_tests/46/test_second_control_stream.py --host localhost --port 4433

Test Structure
--------------

- Each test case is organized in numbered directories (46/, 48/, 50/, etc.)
- Tests follow a consistent pattern: setup → violation → observe response
- All tests extend ``BaseTestClient`` from ``non_conformance_tests/shared/utils.py``

Available Tests
---------------

Core Protocol Violations:
- Test 46: Second control stream 
- Test 48: Client-initiated push stream
- Test 50: DATA frame on control stream
- Test 52: HEADERS frame on control stream
- Test 54: CANCEL_PUSH on request stream
- Test 56: CANCEL_PUSH with invalid push ID
- Test 58: CANCEL_PUSH for unannounced push ID
- Test 60: Second SETTINGS frame
- Test 62: SETTINGS frame on push stream
- Test 63: Duplicate setting identifiers
- Test 65: Reserved setting identifier
- Test 69: Client sends PUSH_PROMISE frame
- Test 71: GOAWAY frame on request stream
- Test 72: MAX_PUSH_ID frame on push stream
- Test 75: Reserved frame type
- Test 77: Forbidden characters in header values (carriage return)
- Test 78: Line feed characters in header values
- Test 79: Null characters in header values

License
-------

BSD 3-Clause License
