"""
K6 performance test runner and configuration management.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from core.src.core.base_util.logger import get_logger
from core.src.core.base_util.exception_handler import BaseTestException

logger = get_logger(__name__)


class K6Error(BaseTestException):
    """Exception raised for K6 execution errors."""
    pass


@dataclass
class K6Config:
    """Configuration for K6 performance tests."""
    script_path: str
    virtual_users: int = 10
    duration: str = "30s"
    ramp_up_time: str = "10s"
    ramp_down_time: str = "10s"
    thresholds: Dict[str, List[str]] = None
    environment_vars: Dict[str, str] = None
    output_format: str = "json"
    output_file: Optional[str] = None
    prometheus_remote_url: Optional[str] = None
    tags: Dict[str, str] = None


class K6Runner:
    """K6 performance test runner with integrated monitoring."""
    
    def __init__(self, config: K6Config):
        self.config = config
        self.results: Optional[Dict[str, Any]] = None
    
    def generate_k6_script(self, test_scenarios: List[Dict[str, Any]]) -> str:
        """Generate K6 JavaScript test script from scenarios."""
        
        script_template = '''
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');
export let responseTime = new Trend('response_time');
export let requestCount = new Counter('requests');

export let options = {
    stages: [
        { duration: '{{ ramp_up_time }}', target: {{ virtual_users }} },
        { duration: '{{ duration }}', target: {{ virtual_users }} },
        { duration: '{{ ramp_down_time }}', target: 0 },
    ],
    thresholds: {{ thresholds }},
    tags: {{ tags }}
};

// Test scenarios
const scenarios = {{ scenarios }};

export default function() {
    for (let scenario of scenarios) {
        executeScenario(scenario);
        sleep(1);
    }
}

function executeScenario(scenario) {
    let response;
    let params = {
        headers: scenario.headers || {},
        tags: scenario.tags || {}
    };
    
    switch(scenario.method.toUpperCase()) {
        case 'GET':
            response = http.get(scenario.url, params);
            break;
        case 'POST':
            response = http.post(scenario.url, scenario.body || null, params);
            break;
        case 'PUT':
            response = http.put(scenario.url, scenario.body || null, params);
            break;
        case 'DELETE':
            response = http.del(scenario.url, scenario.body || null, params);
            break;
        default:
            console.error(`Unsupported HTTP method: ${scenario.method}`);
            return;
    }
    
    // Custom metrics
    requestCount.add(1);
    responseTime.add(response.timings.duration);
    errorRate.add(response.status >= 400);
    
    // Checks
    let checks = {
        'status is 2xx or 3xx': (r) => r.status >= 200 && r.status < 400,
        'response time < 2000ms': (r) => r.timings.duration < 2000,
    };
    
    if (scenario.checks) {
        Object.assign(checks, scenario.checks);
    }
    
    check(response, checks, { scenario: scenario.name || 'default' });
}
'''
        
        # Replace template variables
        script_content = script_template.replace('{{ ramp_up_time }}', self.config.ramp_up_time)
        script_content = script_content.replace('{{ duration }}', self.config.duration)
        script_content = script_content.replace('{{ ramp_down_time }}', self.config.ramp_down_time)
        script_content = script_content.replace('{{ virtual_users }}', str(self.config.virtual_users))
        script_content = script_content.replace('{{ thresholds }}', json.dumps(self.config.thresholds or {}))
        script_content = script_content.replace('{{ tags }}', json.dumps(self.config.tags or {}))
        script_content = script_content.replace('{{ scenarios }}', json.dumps(test_scenarios))
        
        return script_content
    
    def create_k6_script_file(self, test_scenarios: List[Dict[str, Any]]) -> str:
        """Create K6 script file and return path."""
        script_content = self.generate_k6_script(test_scenarios)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        logger.info(f"K6 script created: {script_path}")
        return script_path
    
    def run_k6_test(self, script_path: Optional[str] = None, 
                    scenarios: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Execute K6 performance test."""
        
        # Use provided script or generate new one
        if script_path is None:
            if scenarios is None:
                raise K6Error("Either script_path or scenarios must be provided")
            script_path = self.create_k6_script_file(scenarios)
        else:
            script_path = self.config.script_path
        
        if not Path(script_path).exists():
            raise K6Error(f"K6 script not found: {script_path}")
        
        # Build K6 command
        cmd = ['k6', 'run']
        
        # Add output options
        if self.config.output_format == 'json' and self.config.output_file:
            cmd.extend(['--out', f'json={self.config.output_file}'])
        elif self.config.prometheus_remote_url:
            cmd.extend(['--out', f'experimental-prometheus-rw={self.config.prometheus_remote_url}'])
        
        # Add environment variables
        if self.config.environment_vars:
            for key, value in self.config.environment_vars.items():
                cmd.extend(['-e', f'{key}={value}'])
        
        # Add tags
        if self.config.tags:
            for key, value in self.config.tags.items():
                cmd.extend(['--tag', f'{key}={value}'])
        
        cmd.append(script_path)
        
        try:
            logger.info(f"Executing K6 test: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = f"K6 test failed: {result.stderr}"
                logger.error(error_msg)
                raise K6Error(error_msg)
            
            # Parse results
            test_results = self._parse_k6_output(result.stdout)
            test_results['command'] = ' '.join(cmd)
            test_results['script_path'] = script_path
            
            self.results = test_results
            logger.info("K6 test completed successfully")
            
            return test_results
            
        except subprocess.TimeoutExpired:
            error_msg = "K6 test timed out"
            logger.error(error_msg)
            raise K6Error(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to execute K6 test: {str(e)}"
            logger.error(error_msg)
            raise K6Error(error_msg)
    
    def _parse_k6_output(self, output: str) -> Dict[str, Any]:
        """Parse K6 output and extract metrics."""
        results = {
            'summary': {},
            'metrics': {},
            'checks': {},
            'raw_output': output
        }
        
        lines = output.split('')
        
        # Extract summary information
        in_summary = False
        for line in lines:
            line = line.strip()
            
            if '✓' in line or '✗' in line:
                # Parse check results
                if '✓' in line:
                    check_name = line.split('✓')[-1].strip()
                    results['checks'][check_name] = {'passed': True}
                elif '✗' in line:
                    check_name = line.split('✗')[-1].strip()
                    results['checks'][check_name] = {'passed': False}
            
            elif 'http_reqs' in line or 'http_req_duration' in line or 'vus' in line:
                # Parse metrics
                parts = line.split()
                if len(parts) >= 2:
                    metric_name = parts[0]
                    metric_value = parts[1]
                    results['metrics'][metric_name] = metric_value
        
        return results
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance test report."""
        if not self.results:
            raise K6Error("No test results available. Run test first.")
        
        report = {
            'test_config': {
                'virtual_users': self.config.virtual_users,
                'duration': self.config.duration,
                'ramp_up_time': self.config.ramp_up_time,
                'ramp_down_time': self.config.ramp_down_time
            },
            'results': self.results,
            'analysis': self._analyze_results(self.results)
        }
        
        return report
    
    def _analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results and provide insights."""
        analysis = {
            'performance_rating': 'unknown',
            'bottlenecks': [],
            'recommendations': []
        }
        
        metrics = results.get('metrics', {})
        
        # Analyze response time
        if 'http_req_duration' in metrics:
            duration_str = metrics['http_req_duration']
            # Extract average response time (simplified parsing)
            if 'avg=' in duration_str:
                avg_time = float(duration_str.split('avg=')[1].split('ms')[0])
                
                if avg_time < 100:
                    analysis['performance_rating'] = 'excellent'
                elif avg_time < 500:
                    analysis['performance_rating'] = 'good'
                elif avg_time < 1000:
                    analysis['performance_rating'] = 'fair'
                    analysis['bottlenecks'].append('Response time is above 500ms')
                    analysis['recommendations'].append('Optimize server response time')
                else:
                    analysis['performance_rating'] = 'poor'
                    analysis['bottlenecks'].append('Response time is above 1 second')
                    analysis['recommendations'].append('Investigate server performance issues')
        
        # Analyze error rate
        checks = results.get('checks', {})
        failed_checks = [name for name, check in checks.items() if not check.get('passed', True)]
        
        if failed_checks:
            analysis['bottlenecks'].extend([f"Failed check: {check}" for check in failed_checks])
            analysis['recommendations'].append('Investigate failed checks and fix underlying issues')
        
        return analysis
    
    def export_results(self, output_path: str, format: str = 'json') -> None:
        """Export test results to file."""
        if not self.results:
            raise K6Error("No test results available. Run test first.")
        
        report = self.generate_performance_report()
        
        with open(output_path, 'w') as f:
            if format.lower() == 'json':
                json.dump(report, f, indent=2)
            else:
                raise K6Error(f"Unsupported export format: {format}")
        
        logger.info(f"Results exported to: {output_path}")
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        # Implement cleanup logic for temporary script files
        logger.debug("K6Runner cleanup completed")