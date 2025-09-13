"""
Grafana dashboard management for performance monitoring.
"""

import json
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

from core.src.core.base_util.logger import get_logger
from core.src.core.base_util.exception_handler import BaseTestException

logger = get_logger(__name__)


class GrafanaError(BaseTestException):
    """Exception raised for Grafana operations."""
    pass


class GrafanaDashboard:
    """Client for managing Grafana dashboards."""
    
    def __init__(self, base_url: str = "http://localhost:3000", 
                 api_key: Optional[str] = None,
                 username: str = "admin", 
                 password: str = "admin"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
        else:
            # Use basic auth
            self.session.auth = (username, password)
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
    
    def create_performance_dashboard(self, title: str = "Performance Test Dashboard",
                                   datasource: str = "prometheus") -> Dict[str, Any]:
        """Create a comprehensive performance monitoring dashboard."""
        
        dashboard_config = {
            "dashboard": {
                "id": None,
                "title": title,
                "tags": ["performance", "k6", "testing"],
                "timezone": "browser",
                "refresh": "10s",
                "time": {
                    "from": "now-30m",
                    "to": "now"
                },
                "panels": [
                    self._create_response_time_panel(datasource),
                    self._create_throughput_panel(datasource),
                    self._create_error_rate_panel(datasource),
                    self._create_active_users_panel(datasource),
                    self._create_cpu_usage_panel(datasource),
                    self._create_memory_usage_panel(datasource)
                ],
                "templating": {
                    "list": []
                },
                "annotations": {
                    "list": []
                },
                "schemaVersion": 27
            },
            "overwrite": True
        }
        
        return self._create_dashboard(dashboard_config)
    
    def _create_response_time_panel(self, datasource: str) -> Dict[str, Any]:
        """Create response time panel configuration."""
        return {
            "id": 1,
            "title": "Response Time",
            "type": "graph",
            "datasource": datasource,
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "targets": [
                {
                    "expr": "histogram_quantile(0.95, sum(rate(k6_http_req_duration_bucket[5m])) by (le))",
                    "legendFormat": "95th percentile",
                    "refId": "A"
                },
                {
                    "expr": "histogram_quantile(0.50, sum(rate(k6_http_req_duration_bucket[5m])) by (le))",
                    "legendFormat": "50th percentile",
                    "refId": "B"
                }
            ],
            "yAxes": [
                {
                    "label": "Time (ms)",
                    "min": 0
                }
            ],
            "xAxes": [
                {
                    "mode": "time"
                }
            ]
        }
    
    def _create_throughput_panel(self, datasource: str) -> Dict[str, Any]:
        """Create throughput panel configuration."""
        return {
            "id": 2,
            "title": "Throughput (Requests/sec)",
            "type": "graph",
            "datasource": datasource,
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "targets": [
                {
                    "expr": "sum(rate(k6_http_reqs[5m]))",
                    "legendFormat": "Requests/sec",
                    "refId": "A"
                }
            ],
            "yAxes": [
                {
                    "label": "Requests/sec",
                    "min": 0
                }
            ]
        }
    
    def _create_error_rate_panel(self, datasource: str) -> Dict[str, Any]:
        """Create error rate panel configuration."""
        return {
            "id": 3,
            "title": "Error Rate (%)",
            "type": "stat",
            "datasource": datasource,
            "gridPos": {"h": 8, "w": 6, "x": 0, "y": 8},
            "targets": [
                {
                    "expr": "sum(rate(k6_http_reqs{status!~\"2..\"}[5m])) / sum(rate(k6_http_reqs[5m])) * 100",
                    "legendFormat": "Error Rate",
                    "refId": "A"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "color": {
                        "mode": "thresholds"
                    },
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": 0},
                            {"color": "yellow", "value": 1},
                            {"color": "red", "value": 5}
                        ]
                    }
                }
            }
        }
    
    def _create_active_users_panel(self, datasource: str) -> Dict[str, Any]:
        """Create active users panel configuration."""
        return {
            "id": 4,
            "title": "Active Virtual Users",
            "type": "graph",
            "datasource": datasource,
            "gridPos": {"h": 8, "w": 6, "x": 6, "y": 8},
            "targets": [
                {
                    "expr": "k6_vus",
                    "legendFormat": "Virtual Users",
                    "refId": "A"
                }
            ]
        }
    
    def _create_cpu_usage_panel(self, datasource: str) -> Dict[str, Any]:
        """Create CPU usage panel configuration."""
        return {
            "id": 5,
            "title": "CPU Usage (%)",
            "type": "graph",
            "datasource": datasource,
            "gridPos": {"h": 8, "w": 6, "x": 12, "y": 8},
            "targets": [
                {
                    "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                    "legendFormat": "CPU Usage",
                    "refId": "A"
                }
            ]
        }
    
    def _create_memory_usage_panel(self, datasource: str) -> Dict[str, Any]:
        """Create memory usage panel configuration."""
        return {
            "id": 6,
            "title": "Memory Usage (%)",
            "type": "graph",
            "datasource": datasource,
            "gridPos": {"h": 8, "w": 6, "x": 18, "y": 8},
            "targets": [
                {
                    "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
                    "legendFormat": "Memory Usage",
                    "refId": "A"
                }
            ]
        }
    
    def _create_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create dashboard in Grafana."""
        url = urljoin(self.base_url + '/', 'api/dashboards/db')
        
        try:
            response = self.session.post(url, json=dashboard_config)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') == 'success':
                logger.info(f"Dashboard created successfully: {result['url']}")
                return result
            else:
                raise GrafanaError(f"Failed to create dashboard: {result}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create Grafana dashboard: {str(e)}"
            logger.error(error_msg)
            raise GrafanaError(error_msg)
    
    def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """Get dashboard by UID."""
        url = urljoin(self.base_url + '/', f'api/dashboards/uid/{uid}')
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Retrieved dashboard: {uid}")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get dashboard {uid}: {str(e)}"
            logger.error(error_msg)
            raise GrafanaError(error_msg)
    
    def delete_dashboard(self, uid: str) -> bool:
        """Delete dashboard by UID."""
        url = urljoin(self.base_url + '/', f'api/dashboards/uid/{uid}')
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('message') == 'Dashboard deleted':
                logger.info(f"Dashboard deleted: {uid}")
                return True
            else:
                logger.warning(f"Unexpected response deleting dashboard: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to delete dashboard {uid}: {str(e)}"
            logger.error(error_msg)
            raise GrafanaError(error_msg)
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all dashboards."""
        url = urljoin(self.base_url + '/', 'api/search')
        
        try:
            response = self.session.get(url, params={'type': 'dash-db'})
            response.raise_for_status()
            
            dashboards = response.json()
            logger.debug(f"Retrieved {len(dashboards)} dashboards")
            return dashboards
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to list dashboards: {str(e)}"
            logger.error(error_msg)
            raise GrafanaError(error_msg)
    
    def create_datasource(self, name: str, datasource_type: str = "prometheus",
                         url: str = "http://localhost:9090") -> Dict[str, Any]:
        """Create a new datasource."""
        datasource_config = {
            "name": name,
            "type": datasource_type,
            "url": url,
            "access": "proxy",
            "isDefault": False
        }
        
        api_url = urljoin(self.base_url + '/', 'api/datasources')
        
        try:
            response = self.session.post(api_url, json=datasource_config)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Datasource created: {name}")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create datasource {name}: {str(e)}"
            logger.error(error_msg)
            raise GrafanaError(error_msg)
    
    def check_health(self) -> bool:
        """Check if Grafana server is healthy."""
        url = urljoin(self.base_url + '/', 'api/health')
        
        try:
            response = self.session.get(url, timeout=5)
            is_healthy = response.status_code == 200
            
            if is_healthy:
                logger.debug("Grafana server is healthy")
            else:
                logger.warning(f"Grafana health check failed: {response.status_code}")
            
            return is_healthy
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Grafana health check failed: {str(e)}")
            return False
    
    def export_dashboard(self, uid: str, output_file: str) -> None:
        """Export dashboard to JSON file."""
        dashboard = self.get_dashboard(uid)
        
        with open(output_file, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        logger.info(f"Dashboard exported to: {output_file}")
    
    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            logger.debug("Grafana client session closed")