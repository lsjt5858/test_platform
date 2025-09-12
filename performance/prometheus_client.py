"""
Prometheus client for metrics collection and querying.
"""

import requests
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urljoin

from core.src.core.base_util.logger import get_logger
from core.src.core.base_util.exception_handler import BaseTestException

logger = get_logger(__name__)


class PrometheusError(BaseTestException):
    """Exception raised for Prometheus operations."""
    pass


class PrometheusClient:
    """Client for interacting with Prometheus server."""
    
    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded'
        })
    
    def query(self, query: str, time: Optional[Union[str, datetime]] = None) -> Dict[str, Any]:
        """Execute instant query against Prometheus."""
        url = urljoin(self.base_url + '/', 'api/v1/query')
        
        params = {'query': query}
        if time:
            if isinstance(time, datetime):
                params['time'] = time.timestamp()
            else:
                params['time'] = time
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result['status'] != 'success':
                raise PrometheusError(f"Query failed: {result.get('error', 'Unknown error')}")
            
            logger.debug(f"Prometheus query executed: {query}")
            return result['data']
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to query Prometheus: {str(e)}"
            logger.error(error_msg)
            raise PrometheusError(error_msg)
    
    def query_range(self, query: str, start: Union[str, datetime], 
                   end: Union[str, datetime], step: str = '15s') -> Dict[str, Any]:
        """Execute range query against Prometheus."""
        url = urljoin(self.base_url + '/', 'api/v1/query_range')
        
        params = {
            'query': query,
            'step': step
        }
        
        # Handle datetime conversion
        if isinstance(start, datetime):
            params['start'] = start.timestamp()
        else:
            params['start'] = start
            
        if isinstance(end, datetime):
            params['end'] = end.timestamp()
        else:
            params['end'] = end
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result['status'] != 'success':
                raise PrometheusError(f"Range query failed: {result.get('error', 'Unknown error')}")
            
            logger.debug(f"Prometheus range query executed: {query}")
            return result['data']
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to execute range query: {str(e)}"
            logger.error(error_msg)
            raise PrometheusError(error_msg)
    
    def get_metrics(self) -> List[str]:
        """Get list of available metrics."""
        url = urljoin(self.base_url + '/', 'api/v1/label/__name__/values')
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            result = response.json()
            
            if result['status'] != 'success':
                raise PrometheusError(f"Failed to get metrics: {result.get('error', 'Unknown error')}")
            
            metrics = result['data']
            logger.debug(f"Retrieved {len(metrics)} metrics from Prometheus")
            return metrics
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to retrieve metrics: {str(e)}"
            logger.error(error_msg)
            raise PrometheusError(error_msg)
    
    def get_targets(self) -> Dict[str, Any]:
        """Get information about discovered targets."""
        url = urljoin(self.base_url + '/', 'api/v1/targets')
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            result = response.json()
            
            if result['status'] != 'success':
                raise PrometheusError(f"Failed to get targets: {result.get('error', 'Unknown error')}")
            
            logger.debug("Retrieved target information from Prometheus")
            return result['data']
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to retrieve targets: {str(e)}"
            logger.error(error_msg)
            raise PrometheusError(error_msg)
    
    def get_performance_metrics(self, duration_minutes: int = 30) -> Dict[str, Any]:
        """Get common performance metrics for the specified duration."""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=duration_minutes)
        
        metrics = {}
        
        # Common performance queries
        queries = {
            'cpu_usage': 'avg(100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100))',
            'memory_usage': 'avg((1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100)',
            'disk_usage': 'avg(100 - ((node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes))',
            'http_request_rate': 'sum(rate(http_requests_total[5m]))',
            'http_error_rate': 'sum(rate(http_requests_total{status=~"4..|5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100',
            'response_time_95th': 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))',
            'active_connections': 'sum(http_connections_active)'
        }
        
        for metric_name, query in queries.items():
            try:
                result = self.query_range(query, start_time, end_time, '1m')
                metrics[metric_name] = result
                logger.debug(f"Retrieved metric: {metric_name}")
            except Exception as e:
                logger.warning(f"Failed to retrieve metric {metric_name}: {str(e)}")
                metrics[metric_name] = None
        
        return metrics
    
    def check_health(self) -> bool:
        """Check if Prometheus server is healthy."""
        url = urljoin(self.base_url + '/', '-/healthy')
        
        try:
            response = self.session.get(url, timeout=5)
            is_healthy = response.status_code == 200
            
            if is_healthy:
                logger.debug("Prometheus server is healthy")
            else:
                logger.warning(f"Prometheus server health check failed: {response.status_code}")
            
            return is_healthy
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Prometheus health check failed: {str(e)}")
            return False
    
    def get_build_info(self) -> Dict[str, Any]:
        """Get Prometheus server build information."""
        try:
            result = self.query('prometheus_build_info')
            
            if result['result']:
                build_info = result['result'][0]['metric']
                logger.debug(f"Prometheus build info: {build_info}")
                return build_info
            else:
                return {}
                
        except Exception as e:
            logger.warning(f"Failed to get Prometheus build info: {str(e)}")
            return {}
    
    def create_alert_query(self, metric: str, threshold: float, 
                          operator: str = '>', duration: str = '5m') -> str:
        """Create alert query for monitoring."""
        query_templates = {
            '>': f'{metric} {operator} {threshold}',
            '<': f'{metric} {operator} {threshold}',
            '>=': f'{metric} {operator} {threshold}',
            '<=': f'{metric} {operator} {threshold}',
            '==': f'{metric} {operator} {threshold}',
            '!=': f'{metric} {operator} {threshold}'
        }
        
        base_query = query_templates.get(operator, f'{metric} > {threshold}')
        alert_query = f'{base_query} for {duration}'
        
        logger.debug(f"Created alert query: {alert_query}")
        return alert_query
    
    def export_metrics(self, queries: Dict[str, str], start_time: datetime, 
                      end_time: datetime, output_file: str) -> None:
        """Export metrics data to file."""
        import json
        
        exported_data = {
            'export_time': datetime.now().isoformat(),
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'metrics': {}
        }
        
        for metric_name, query in queries.items():
            try:
                result = self.query_range(query, start_time, end_time, '1m')
                exported_data['metrics'][metric_name] = result
                logger.debug(f"Exported metric: {metric_name}")
            except Exception as e:
                logger.warning(f"Failed to export metric {metric_name}: {str(e)}")
                exported_data['metrics'][metric_name] = {'error': str(e)}
        
        with open(output_file, 'w') as f:
            json.dump(exported_data, f, indent=2)
        
        logger.info(f"Metrics exported to: {output_file}")
    
    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            logger.debug("Prometheus client session closed")