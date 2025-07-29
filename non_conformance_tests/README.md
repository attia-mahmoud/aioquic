# HTTP/3 Non-Conformance Tests

A comprehensive suite of tests designed to evaluate how HTTP/3 proxies, servers, and other implementations handle protocol violations and edge cases.

## Overview

This test suite systematically violates HTTP/3 specifications to:
- **Test proxy robustness** against malformed traffic
- **Identify security vulnerabilities** in HTTP/3 implementations
- **Document implementation differences** across vendors
- **Validate error handling** according to RFC specifications
- **Research attack vectors** for security analysis

## Test Organization

Each test case is organized in numbered directories with comprehensive documentation:

```
non_conformance_tests/
├── 1/                          # PRIORITY_UPDATE before SETTINGS
│   ├── test_priority_update_first_frame.py
│   └── README.md
├── 2/                          # [Future test case]
├── 3/                          # [Future test case]
├── shared/                     # Shared utilities
│   ├── test_server.py         # Common test server
│   └── utils.py               # Helper functions
└── README.md                  # This file
```

## Current Test Cases

### ✅ Test Case #1: PRIORITY_UPDATE Before SETTINGS
**Violation**: RFC 9114 Section 6.2.1 - SETTINGS must be first frame on control stream

**Description**: Sends PRIORITY_UPDATE frame as the first frame on the HTTP control stream instead of the required SETTINGS frame.

**Status**: ✅ Implemented  
**Directory**: `1/`

### ✅ Test Case #3: Multiple Requests on Same Stream
**Violation**: RFC 9114 Section 4.1 - Client must send only single request per stream

**Description**: Sends two HEADERS frames that each look like independent requests on the same stream.

**Status**: ✅ Implemented  
**Directory**: `3/`

### ✅ Test Case #5: DATA Frame Before HEADERS
**Violation**: Invalid frame sequence - DATA before HEADERS triggers H3_FRAME_UNEXPECTED

**Description**: Sends DATA frame on request stream without preceding HEADERS frame.

**Status**: ✅ Implemented  
**Directory**: `5/`

## Prerequisites

### Modified aioquic Installation
These tests require a modified version of aioquic with relaxed protocol validation:

```bash
# Install in development mode
cd /path/to/aioquic
pip install -e .
```

### Required Modifications
The following changes have been made to `src/aioquic/h3/connection.py`:
- Added `skip_settings_frame` parameter to H3Connection
- Commented out various protocol assertions for non-conformance testing
- Added custom H3CustomAPI for manual frame control

## Quick Start

### 1. Start Test Server (Optional)
For local testing, start the provided test server:

```bash
python examples/h3_test_server.py &
```

### 2. Run Individual Test Cases
```bash
# Test Case 1: PRIORITY_UPDATE before SETTINGS
python non_conformance_tests/1/test_priority_update_first_frame.py

# Test Case 3: Multiple requests on same stream
python non_conformance_tests/3/test_multiple_requests_same_stream.py

# Test Case 5: DATA frame before HEADERS
python non_conformance_tests/5/test_data_frame_before_headers.py

# Test against specific target
python non_conformance_tests/1/test_priority_update_first_frame.py --host proxy.example.com --port 443
python non_conformance_tests/3/test_multiple_requests_same_stream.py --host proxy.example.com --port 443
python non_conformance_tests/5/test_data_frame_before_headers.py --host proxy.example.com --port 443
```

### 3. Run All Tests
```bash
# Coming soon: test runner script
python non_conformance_tests/run_all_tests.py
```

## Test Architecture

### Core Components

#### 1. H3CustomAPI (`src/aioquic/h3/custom_api.py`)
Provides atomic operations for manual HTTP/3 frame control:
- Manual stream creation
- Raw frame sending
- Bypass protocol constraints
- Fine-grained control over frame order

#### 2. Test Framework
Each test case follows a standardized structure:
- **Setup**: QUIC connection establishment
- **Violation**: Execute specific protocol violation
- **Observation**: Monitor proxy/server response
- **Analysis**: Document behavior and error codes

#### 3. Test Server (`examples/h3_test_server.py`)
Logs all HTTP/3 events for analysis:
- Non-conformant frame handling
- Connection termination behavior
- Error code reporting

### Test Case Structure

```python
class TestCaseXClient:
    async def run_test(self, host, port):
        # 1. Establish connection
        # 2. Execute violation
        # 3. Observe behavior
        # 4. Report results
        
    async def _step_violation(self):
        # Specific protocol violation
        pass
```

## Target Analysis

### Proxy Behaviors to Test

#### 🎯 Error Handling
- Connection termination timing
- Error code accuracy (per RFC 9114)
- Error message propagation
- Recovery mechanisms

#### 🎯 Security Response
- DoS resilience against malformed frames
- Resource exhaustion protection
- Invalid state handling
- Buffer overflow protection

#### 🎯 Compliance Levels
- Strict RFC compliance vs. lenient handling
- Vendor-specific behaviors
- Version differences
- Configuration impact

### Common Test Targets

- **Proxies**: nginx, HAProxy, Envoy, Cloudflare
- **Servers**: Apache, nginx, Node.js, Go
- **Load Balancers**: AWS ALB, GCP Load Balancer
- **CDNs**: Cloudflare, Fastly, AWS CloudFront

## Running Tests Against Real Targets

### Example Test Scenarios

```bash
# Test Cloudflare's HTTP/3 implementation
python non_conformance_tests/1/test_priority_update_first_frame.py \
    --host cloudflare.com --port 443

# Test against local nginx-quic
python non_conformance_tests/1/test_priority_update_first_frame.py \
    --host localhost --port 8443

# Test with verbose logging for analysis
python non_conformance_tests/1/test_priority_update_first_frame.py \
    --host target.example.com --port 443 --verbose
```

### Results Documentation

Create detailed reports for each target:
- Connection behavior logs
- Error codes and messages  
- Timing analysis
- Comparison with RFC requirements

## Contributing

### Adding New Test Cases

1. **Create Test Directory**:
   ```bash
   mkdir non_conformance_tests/{next_number}
   ```

2. **Implement Test**:
   - Copy template from existing test
   - Modify violation logic
   - Update documentation

3. **Document Violation**:
   - RFC section reference
   - Expected vs. actual behavior
   - Analysis guidelines

### Test Case Template

```python
class TestCaseXClient:
    """Test Case X: [Brief Description]"""
    
    def __init__(self):
        self.test_results = {...}
    
    async def run_test(self, host, port):
        """Execute Test Case X: [Violation Description]"""
        # Standard test structure
        pass
    
    async def _step_execute_violation(self):
        """Execute the specific protocol violation"""
        # Custom violation logic
        pass
```

## Security Considerations

⚠️ **Warning**: These tests intentionally violate HTTP/3 specifications and may:
- Cause target systems to terminate connections
- Trigger security monitoring systems
- Be flagged as malicious traffic
- Impact system performance

### Responsible Testing

- **Get Permission**: Only test systems you own or have explicit permission to test
- **Document Everything**: Keep detailed logs of all test activities
- **Respect Rate Limits**: Don't overwhelm target systems
- **Report Vulnerabilities**: Responsibly disclose any security issues found

## References

### HTTP/3 Specifications
- [RFC 9114 - HTTP/3](https://datatracker.ietf.org/doc/html/rfc9114)
- [RFC 9000 - QUIC Transport Protocol](https://datatracker.ietf.org/doc/html/rfc9000)
- [RFC 9218 - HTTP Prioritization](https://datatracker.ietf.org/doc/html/rfc9218)

### Implementation References
- [aioquic Documentation](https://aioquic.readthedocs.io/)
- [QUIC Working Group](https://quicwg.org/)
- [HTTP/3 Explained](https://http3-explained.haxx.se/)

## License

This test suite is part of the aioquic project and follows the same BSD license terms.

---

**⚡ Happy Testing!** Remember to test responsibly and document your findings for the benefit of the HTTP/3 community. 