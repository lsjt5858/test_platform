#!/usr/bin/env python3
"""
K6 to Pushgateway Bridge
Reads K6 CSV output and pushes metrics to Pushgateway
"""
import csv
import time
import requests
import os
from collections import defaultdict
import sys

def parse_k6_csv(csv_file):
    """Parse K6 CSV output and aggregate metrics"""
    metrics = defaultdict(list)
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['metric_name'] and row['metric_value']:
                    value = float(row['metric_value'])
                    
                    # Create metric key with labels - only include meaningful labels
                    labels = []
                    if row.get('url') and row['url'].strip():
                        labels.append(f'url="{row["url"]}"')
                    if row.get('method') and row['method'].strip():
                        labels.append(f'method="{row["method"]}"')
                    if row.get('status') and row['status'].strip():
                        labels.append(f'status="{row["status"]}"')
                    if row.get('scenario') and row['scenario'].strip():
                        labels.append(f'scenario="{row["scenario"]}"')
                    if row.get('check') and row['check'].strip():
                        labels.append(f'check="{row["check"]}"')
                    
                    label_str = '{' + ','.join(labels) + '}' if labels else ''
                    metric_key = f'k6_{row["metric_name"]}{label_str}'
                    
                    metrics[metric_key].append(value)
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return {}
    
    return metrics

def aggregate_metrics(metrics):
    """Aggregate metrics by taking the latest value or sum for counters"""
    aggregated = {}
    
    for metric_name, values in metrics.items():
        if not values:
            continue
            
        # For counter-like metrics, use the last value (cumulative)
        if any(counter_type in metric_name for counter_type in ['http_reqs', 'iterations', 'checks', 'data_sent', 'data_received']):
            aggregated[metric_name] = values[-1]  # Last value for counters
        # For gauge-like metrics, use the last value
        elif any(gauge_type in metric_name for gauge_type in ['vus', 'vus_max']):
            aggregated[metric_name] = values[-1]  # Current value for gauges
        # For timing metrics, use average
        else:
            aggregated[metric_name] = sum(values) / len(values) if values else 0
    
    return aggregated

def send_to_pushgateway(metrics, pushgateway_url):
    """Send metrics to Pushgateway"""
    if not metrics:
        print("No metrics to send")
        return False
    
    # Create Pushgateway payload in text format
    payload_lines = []
    
    for metric_name, value in metrics.items():
        payload_lines.append(f"{metric_name} {value}")
    
    payload = '\n'.join(payload_lines) + '\n'
    
    # Push to Pushgateway
    job_name = "k6_performance_test"
    url = f"{pushgateway_url}/metrics/job/{job_name}/instance/k6_test"
    
    try:
        response = requests.post(
            url,
            data=payload,
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        response.raise_for_status()
        print(f"Successfully sent {len(metrics)} metrics to Pushgateway")
        print(f"Payload preview:")
        for line in payload_lines[:5]:  # Show first 5 metrics
            print(f"  {line}")
        if len(payload_lines) > 5:
            print(f"  ... and {len(payload_lines) - 5} more metrics")
        return True
    except Exception as e:
        print(f"Failed to send metrics to Pushgateway: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return False

def main():
    csv_file = "/results/k6_results.csv"
    pushgateway_url = "http://pushgateway:9091"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        pushgateway_url = sys.argv[2]
    
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        sys.exit(1)
    
    print(f"Parsing K6 results from: {csv_file}")
    raw_metrics = parse_k6_csv(csv_file)
    
    if not raw_metrics:
        print("No metrics found in CSV file")
        sys.exit(1)
    
    print(f"Found {len(raw_metrics)} raw metric entries")
    
    # Aggregate metrics
    metrics = aggregate_metrics(raw_metrics)
    print(f"Aggregated to {len(metrics)} unique metrics")
    
    print(f"Sending metrics to Pushgateway at: {pushgateway_url}")
    if send_to_pushgateway(metrics, pushgateway_url):
        print("Metrics successfully sent to Pushgateway!")
    else:
        print("Failed to send metrics to Pushgateway")
        sys.exit(1)

if __name__ == "__main__":
    main()