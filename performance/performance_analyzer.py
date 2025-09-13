"""
Performance analysis and reporting utilities.
"""

import json
import statistics
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from core.src.core.base_util.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    response_times: List[float]
    throughput: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    active_users: int
    duration_seconds: float


@dataclass
class PerformanceThresholds:
    """Performance thresholds for analysis."""
    max_response_time: float = 2000.0  # ms
    min_throughput: float = 100.0      # requests/sec
    max_error_rate: float = 1.0        # %
    max_cpu_usage: float = 80.0        # %
    max_memory_usage: float = 80.0     # %


class PerformanceAnalyzer:
    """Comprehensive performance analysis and reporting."""
    
    def __init__(self, thresholds: Optional[PerformanceThresholds] = None):
        self.thresholds = thresholds or PerformanceThresholds()
        
    def analyze_k6_results(self, k6_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze K6 test results."""
        analysis = {
            'summary': {},
            'performance_score': 0,
            'issues': [],
            'recommendations': [],
            'passed_checks': [],
            'failed_checks': []
        }
        
        # Analyze metrics
        metrics = k6_results.get('metrics', {})
        
        # Response time analysis
        if 'http_req_duration' in metrics:
            response_time_analysis = self._analyze_response_times(metrics['http_req_duration'])
            analysis['summary']['response_time'] = response_time_analysis
            
            if response_time_analysis.get('p95', 0) > self.thresholds.max_response_time:
                analysis['issues'].append(
                    f"95th percentile response time ({response_time_analysis.get('p95', 0):.2f}ms) "
                    f"exceeds threshold ({self.thresholds.max_response_time}ms)"
                )
                analysis['recommendations'].append("Optimize server response time")
        
        # Throughput analysis
        if 'http_reqs' in metrics:
            throughput_analysis = self._analyze_throughput(metrics['http_reqs'])
            analysis['summary']['throughput'] = throughput_analysis
            
            if throughput_analysis.get('rate', 0) < self.thresholds.min_throughput:
                analysis['issues'].append(
                    f"Throughput ({throughput_analysis.get('rate', 0):.2f} req/s) "
                    f"below threshold ({self.thresholds.min_throughput} req/s)"
                )
                analysis['recommendations'].append("Scale up server capacity")
        
        # Check analysis
        checks = k6_results.get('checks', {})
        for check_name, check_result in checks.items():
            if check_result.get('passed', False):
                analysis['passed_checks'].append(check_name)
            else:
                analysis['failed_checks'].append(check_name)
                analysis['issues'].append(f"Failed check: {check_name}")
        
        # Calculate performance score
        analysis['performance_score'] = self._calculate_performance_score(analysis)
        
        return analysis
    
    def _analyze_response_times(self, duration_metric: str) -> Dict[str, float]:
        """Analyze response time metrics from K6 output."""
        # Parse K6 duration metric (simplified)
        # Format: "avg=123.45ms min=12.34ms med=56.78ms max=234.56ms p(90)=178.90ms p(95)=201.23ms"
        
        analysis = {}
        
        try:
            # Extract values using string parsing
            parts = duration_metric.split(' ')
            for part in parts:
                if '=' in part:
                    key, value = part.split('=')
                    # Remove 'ms' suffix and convert to float
                    numeric_value = float(value.replace('ms', ''))
                    
                    if key == 'avg':
                        analysis['average'] = numeric_value
                    elif key == 'min':
                        analysis['minimum'] = numeric_value
                    elif key == 'med':
                        analysis['median'] = numeric_value
                    elif key == 'max':
                        analysis['maximum'] = numeric_value
                    elif key == 'p(90)':
                        analysis['p90'] = numeric_value
                    elif key == 'p(95)':
                        analysis['p95'] = numeric_value
            
        except Exception as e:
            logger.warning(f"Failed to parse response time metrics: {str(e)}")
            analysis = {'error': 'Failed to parse metrics'}
        
        return analysis
    
    def _analyze_throughput(self, reqs_metric: str) -> Dict[str, float]:
        """Analyze throughput metrics from K6 output."""
        analysis = {}
        
        try:
            # Parse requests metric
            # Format might include total requests and rate
            if 'rate=' in reqs_metric:
                rate_part = reqs_metric.split('rate=')[1].split(' ')[0]
                analysis['rate'] = float(rate_part.replace('/s', ''))
            
            if 'total=' in reqs_metric:
                total_part = reqs_metric.split('total=')[1].split(' ')[0]
                analysis['total'] = int(total_part)
                
        except Exception as e:
            logger.warning(f"Failed to parse throughput metrics: {str(e)}")
            analysis = {'error': 'Failed to parse metrics'}
        
        return analysis
    
    def _calculate_performance_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall performance score (0-100)."""
        score = 100
        
        # Deduct points for issues
        issues_count = len(analysis.get('issues', []))
        score -= min(issues_count * 15, 60)  # Max 60 points deduction for issues
        
        # Deduct points for failed checks
        failed_checks = len(analysis.get('failed_checks', []))
        score -= min(failed_checks * 10, 30)  # Max 30 points deduction for failed checks
        
        # Bonus points for passing all checks
        if not analysis.get('failed_checks') and analysis.get('passed_checks'):
            score += 10
        
        return max(score, 0)  # Ensure score is not negative
    
    def compare_performance_runs(self, baseline: Dict[str, Any], 
                                current: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two performance test runs."""
        comparison = {
            'regression_detected': False,
            'improvements': [],
            'degradations': [],
            'summary': {}
        }
        
        # Compare response times
        baseline_rt = baseline.get('summary', {}).get('response_time', {})
        current_rt = current.get('summary', {}).get('response_time', {})
        
        if baseline_rt.get('average') and current_rt.get('average'):
            rt_change = ((current_rt['average'] - baseline_rt['average']) / 
                        baseline_rt['average']) * 100
            
            comparison['summary']['response_time_change'] = rt_change
            
            if rt_change > 10:  # 10% degradation threshold
                comparison['degradations'].append(
                    f"Response time increased by {rt_change:.1f}%"
                )
                comparison['regression_detected'] = True
            elif rt_change < -5:  # 5% improvement threshold
                comparison['improvements'].append(
                    f"Response time improved by {abs(rt_change):.1f}%"
                )
        
        # Compare throughput
        baseline_tp = baseline.get('summary', {}).get('throughput', {})
        current_tp = current.get('summary', {}).get('throughput', {})
        
        if baseline_tp.get('rate') and current_tp.get('rate'):
            tp_change = ((current_tp['rate'] - baseline_tp['rate']) / 
                        baseline_tp['rate']) * 100
            
            comparison['summary']['throughput_change'] = tp_change
            
            if tp_change < -10:  # 10% degradation threshold
                comparison['degradations'].append(
                    f"Throughput decreased by {abs(tp_change):.1f}%"
                )
                comparison['regression_detected'] = True
            elif tp_change > 5:  # 5% improvement threshold
                comparison['improvements'].append(
                    f"Throughput improved by {tp_change:.1f}%"
                )
        
        # Compare error rates
        baseline_errors = len(baseline.get('failed_checks', []))
        current_errors = len(current.get('failed_checks', []))
        
        if current_errors > baseline_errors:
            comparison['degradations'].append(
                f"Error count increased from {baseline_errors} to {current_errors}"
            )
            comparison['regression_detected'] = True
        elif current_errors < baseline_errors:
            comparison['improvements'].append(
                f"Error count decreased from {baseline_errors} to {current_errors}"
            )
        
        return comparison
    
    def generate_performance_report(self, analysis: Dict[str, Any],
                                   test_config: Dict[str, Any] = None,
                                   comparison: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'test_configuration': test_config or {},
            'performance_score': analysis.get('performance_score', 0),
            'summary': analysis.get('summary', {}),
            'issues': analysis.get('issues', []),
            'recommendations': analysis.get('recommendations', []),
            'check_results': {
                'passed': analysis.get('passed_checks', []),
                'failed': analysis.get('failed_checks', [])
            },
            'comparison': comparison,
            'verdict': self._get_performance_verdict(analysis.get('performance_score', 0))
        }
        
        return report
    
    def _get_performance_verdict(self, score: int) -> str:
        """Get performance verdict based on score."""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Fair"
        elif score >= 60:
            return "Poor"
        else:
            return "Critical"
    
    def export_report(self, report: Dict[str, Any], output_file: str,
                     format: str = 'json') -> None:
        """Export performance report to file."""
        
        if format.lower() == 'json':
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
        elif format.lower() == 'html':
            self._export_html_report(report, output_file)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Performance report exported to: {output_file}")
    
    def _export_html_report(self, report: Dict[str, Any], output_file: str) -> None:
        """Export report as HTML."""
        html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Performance Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .score { font-size: 24px; font-weight: bold; }
        .excellent { color: #4CAF50; }
        .good { color: #8BC34A; }
        .fair { color: #FF9800; }
        .poor { color: #F44336; }
        .critical { color: #D32F2F; }
        .section { margin: 20px 0; }
        .issues { color: #F44336; }
        .improvements { color: #4CAF50; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Performance Test Report</h1>
        <p>Generated: {{ timestamp }}</p>
        <p class="score {{ verdict_class }}">
            Performance Score: {{ score }}/100 ({{ verdict }})
        </p>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        {{ summary_html }}
    </div>
    
    <div class="section">
        <h2>Issues</h2>
        {{ issues_html }}
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        {{ recommendations_html }}
    </div>
    
    <div class="section">
        <h2>Check Results</h2>
        {{ checks_html }}
    </div>
</body>
</html>
        '''
        
        # Format the template (simplified implementation)
        html_content = html_template.replace('{{ timestamp }}', report['report_timestamp'])
        html_content = html_content.replace('{{ score }}', str(report['performance_score']))
        html_content = html_content.replace('{{ verdict }}', report['verdict'])
        html_content = html_content.replace('{{ verdict_class }}', report['verdict'].lower())
        
        # Add sections (simplified)
        html_content = html_content.replace('{{ summary_html }}', '<pre>' + json.dumps(report['summary'], indent=2) + '</pre>')
        html_content = html_content.replace('{{ issues_html }}', '<ul>' + ''.join([f'<li>{issue}</li>' for issue in report['issues']]) + '</ul>')
        html_content = html_content.replace('{{ recommendations_html }}', '<ul>' + ''.join([f'<li>{rec}</li>' for rec in report['recommendations']]) + '</ul>')
        html_content = html_content.replace('{{ checks_html }}', f"<p>Passed: {len(report['check_results']['passed'])}, Failed: {len(report['check_results']['failed'])}</p>")
        
        with open(output_file, 'w') as f:
            f.write(html_content)