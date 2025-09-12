"""
Test runner utilities for coordinated test execution.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import subprocess
import sys

from ..base_util.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TestConfig:
    """Configuration for test execution."""
    test_paths: List[str]
    markers: Optional[List[str]] = None
    workers: int = 1
    verbose: bool = True
    capture: str = "no"
    html_report: Optional[str] = None
    junit_xml: Optional[str] = None
    coverage: bool = False
    coverage_report: Optional[str] = None


class TestRunner:
    """Enhanced pytest runner with reporting and parallel execution."""
    
    def __init__(self, config: TestConfig):
        self.config = config
    
    def run_tests(self) -> int:
        """Execute tests with configuration."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test paths
        cmd.extend(self.config.test_paths)
        
        # Add options
        if self.config.verbose:
            cmd.append("-v")
        
        cmd.extend(["-s", f"--capture={self.config.capture}"])
        
        if self.config.workers > 1:
            cmd.extend(["-n", str(self.config.workers)])
        
        if self.config.markers:
            for marker in self.config.markers:
                cmd.extend(["-m", marker])
        
        if self.config.html_report:
            cmd.extend([f"--html={self.config.html_report}"])
        
        if self.config.junit_xml:
            cmd.extend([f"--junit-xml={self.config.junit_xml}"])
        
        if self.config.coverage:
            cmd.append("--cov")
            if self.config.coverage_report:
                cmd.extend([f"--cov-report={self.config.coverage_report}"])
        
        logger.info(f"Running tests with command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode