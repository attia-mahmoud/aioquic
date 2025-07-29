#!/usr/bin/env python3

"""
Comprehensive Test Runner for HTTP/3 Non-Conformance Tests

This script automatically:
1. Starts the test server
2. Runs all non-conformance tests in sequence
3. Logs results to a file
4. Provides a summary of passing/failing tests
"""

import asyncio
import glob
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_runner")


class TestResult:
    """Container for individual test results."""
    
    def __init__(self, test_id: str, test_file: str):
        self.test_id = test_id
        self.test_file = test_file
        self.success = False
        self.output = ""
        self.error_output = ""
        self.execution_time = 0.0
        self.exception = None


class TestRunner:
    """Main test runner class."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.log_file = self.base_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.server_process: Optional[subprocess.Popen] = None
        self.test_results: Dict[str, TestResult] = {}
        
    def find_all_tests(self) -> List[Tuple[str, str]]:
        """Find all test files in numbered directories."""
        tests = []
        
        # Look for numbered directories
        for item in self.base_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                test_id = item.name
                # Find Python test file in this directory
                test_files = list(item.glob("test_*.py"))
                if test_files:
                    test_file = test_files[0]  # Take the first one
                    tests.append((test_id, str(test_file)))
                else:
                    logger.warning(f"No test file found in directory {test_id}")
        
        # Sort by test ID number
        tests.sort(key=lambda x: int(x[0]))
        return tests
    
    async def start_test_server(self) -> bool:
        """Start the test server in the background."""
        try:
            server_script = self.base_dir / "shared" / "test_server.py"
            if not server_script.exists():
                logger.error(f"Test server script not found: {server_script}")
                return False
            
            logger.info("🚀 Starting test server...")
            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir),
                text=True
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(3)
            
            # Check if server is still running
            if self.server_process.poll() is None:
                logger.info("✅ Test server started successfully")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"❌ Test server failed to start:")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting test server: {e}")
            return False
    
    def stop_test_server(self):
        """Stop the test server."""
        if self.server_process:
            logger.info("🛑 Stopping test server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                logger.info("✅ Test server stopped")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Server didn't stop gracefully, killing...")
                self.server_process.kill()
                self.server_process.wait()
            self.server_process = None
    
    async def run_single_test(self, test_id: str, test_file: str) -> TestResult:
        """Run a single test and capture its output."""
        result = TestResult(test_id, test_file)
        
        try:
            logger.info(f"🧪 Running Test Case #{test_id}: {Path(test_file).name}")
            
            start_time = time.time()
            
            # Run the test
            process = await asyncio.create_subprocess_exec(
                sys.executable, test_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.base_dir)
            )
            
            stdout, stderr = await process.communicate()
            
            result.execution_time = time.time() - start_time
            result.output = stdout.decode('utf-8', errors='replace')
            result.error_output = stderr.decode('utf-8', errors='replace')
            result.success = process.returncode == 0
            
            if result.success:
                logger.info(f"✅ Test Case #{test_id} PASSED ({result.execution_time:.2f}s)")
            else:
                logger.warning(f"❌ Test Case #{test_id} FAILED ({result.execution_time:.2f}s)")
            
        except Exception as e:
            result.exception = str(e)
            result.success = False
            logger.error(f"💥 Test Case #{test_id} CRASHED: {e}")
        
        return result
    
    def write_log_file(self):
        """Write detailed results to log file."""
        try:
            with open(self.log_file, 'w') as f:
                f.write("HTTP/3 Non-Conformance Test Results\n")
                f.write("=" * 50 + "\n")
                f.write(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Tests: {len(self.test_results)}\n")
                
                passed = sum(1 for r in self.test_results.values() if r.success)
                failed = len(self.test_results) - passed
                f.write(f"Passed: {passed}\n")
                f.write(f"Failed: {failed}\n\n")
                
                # Write detailed results for each test
                for test_id in sorted(self.test_results.keys(), key=int):
                    result = self.test_results[test_id]
                    f.write(f"\n{'='*60}\n")
                    f.write(f"TEST CASE #{test_id}: {Path(result.test_file).name}\n")
                    f.write(f"{'='*60}\n")
                    f.write(f"Status: {'PASSED' if result.success else 'FAILED'}\n")
                    f.write(f"Execution Time: {result.execution_time:.2f}s\n")
                    
                    if result.exception:
                        f.write(f"Exception: {result.exception}\n")
                    
                    f.write(f"\nSTDOUT:\n{'-'*30}\n")
                    f.write(result.output)
                    
                    if result.error_output:
                        f.write(f"\nSTDERR:\n{'-'*30}\n")
                        f.write(result.error_output)
                    
                    f.write(f"\n{'-'*60}\n")
            
            logger.info(f"📄 Detailed results written to: {self.log_file}")
            
        except Exception as e:
            logger.error(f"❌ Error writing log file: {e}")
    
    def print_summary(self):
        """Print a summary of test results."""
        print("\n" + "=" * 80)
        print("🧪 HTTP/3 NON-CONFORMANCE TEST SUMMARY")
        print("=" * 80)
        
        if not self.test_results:
            print("❌ No tests were executed")
            return
        
        passed_tests = []
        failed_tests = []
        
        for test_id in sorted(self.test_results.keys(), key=int):
            result = self.test_results[test_id]
            if result.success:
                passed_tests.append(test_id)
            else:
                failed_tests.append(test_id)
        
        total_tests = len(self.test_results)
        total_time = sum(r.execution_time for r in self.test_results.values())
        
        print(f"📊 Results: {len(passed_tests)}/{total_tests} tests passed")
        print(f"⏱️  Total execution time: {total_time:.2f}s")
        print()
        
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test_id in passed_tests:
                result = self.test_results[test_id]
                test_name = Path(result.test_file).name
                print(f"   #{test_id:>2}: {test_name} ({result.execution_time:.2f}s)")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test_id in failed_tests:
                result = self.test_results[test_id]
                test_name = Path(result.test_file).name
                reason = "Exception" if result.exception else "Non-zero exit code"
                print(f"   #{test_id:>2}: {test_name} ({reason})")
        
        print("\n" + "=" * 80)
        print(f"📄 Detailed logs saved to: {self.log_file}")
        print("=" * 80)
    
    async def run_all_tests(self):
        """Main method to run all tests."""
        try:
            print("🚀 HTTP/3 Non-Conformance Test Runner")
            print("=" * 50)
            
            # Find all tests
            tests = self.find_all_tests()
            if not tests:
                logger.error("❌ No tests found!")
                return False
            
            logger.info(f"📋 Found {len(tests)} test cases")
            
            # Start test server
            if not await self.start_test_server():
                logger.error("❌ Failed to start test server")
                return False
            
            try:
                # Run each test
                for test_id, test_file in tests:
                    result = await self.run_single_test(test_id, test_file)
                    self.test_results[test_id] = result
                    
                    # Small delay between tests
                    await asyncio.sleep(1)
                
                # Write results and print summary
                self.write_log_file()
                self.print_summary()
                
                return True
                
            finally:
                # Always stop the server
                self.stop_test_server()
                
        except KeyboardInterrupt:
            logger.info("🛑 Test run interrupted by user")
            self.stop_test_server()
            return False
        except Exception as e:
            logger.error(f"💥 Test runner crashed: {e}")
            self.stop_test_server()
            return False


async def main():
    """Main entry point."""
    runner = TestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 