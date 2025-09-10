#!/usr/bin/env python3
"""
K6 to Prometheus Bridge
Reads K6 CSV output and pushes metrics to Prometheus via remote write API
"""
import csv
import time
import requests
import json
from collections import defaultdict
import sys
import os

def parse_k6_csv(csv_file):
    """Parse K6 CSV output and convert to Prometheus format"""
    metrics = defaultdict(list)
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['metric_name'] and row['metric_value']:
                    timestamp = int(float(row['timestamp']) * 1000)  # Convert to milliseconds
                    value = float(row['metric_value'])
                    
                    # Create metric labels
                    labels = {}
                    if row.get('url'):
                        labels['url'] = row['url']
                    if row.get('method'):
                        labels['method'] = row['method']
                    if row.get('status'):
                        labels['status'] = row['status']
                    if row.get('scenario'):
                        labels['scenario'] = row['scenario']
                    
                    metrics[row['metric_name']].append({
                        'timestamp': timestamp,
                        'value': value,
                        'labels': labels
                    })
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return {}
    
    return metrics

def send_to_prometheus(metrics, prometheus_url):
    """Send metrics to Prometheus via remote write API"""
    time_series = []
    
    for metric_name, data_points in metrics.items():
        for point in data_points:
            labels = [
                {'name': '__name__', 'value': f'k6_{metric_name}'},
            ]
            
            # Add custom labels
            for label_name, label_value in point['labels'].items():
                labels.append({'name': label_name, 'value': str(label_value)})
            
            time_series.append({
                'labels': labels,
                'samples': [
                    {
                        'value': point['value'],
                        'timestamp': point['timestamp']
                    }
                ]
            })
    
    # Prepare remote write request
    payload = {
        'timeseries': time_series
    }
    
    try:
        response = requests.post(
            f"{prometheus_url}/api/v1/write",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        print(f"Successfully sent {len(time_series)} metrics to Prometheus")
        return True
    except Exception as e:
        print(f"Failed to send metrics to Prometheus: {e}")
        return False

def main():
    csv_file = "/results/k6_results.csv"
    prometheus_url = "http://prometheus:9090"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        prometheus_url = sys.argv[2]
    
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        sys.exit(1)
    
    print(f"Parsing K6 results from: {csv_file}")
    metrics = parse_k6_csv(csv_file)
    
    if not metrics:
        print("No metrics found in CSV file")
        sys.exit(1)
    
    print(f"Found {len(metrics)} metric types")
    for metric_name, points in metrics.items():
        print(f"  - {metric_name}: {len(points)} data points")
    
    print(f"Sending metrics to Prometheus at: {prometheus_url}")
    if send_to_prometheus(metrics, prometheus_url):
        print("Metrics successfully sent to Prometheus!")
    else:
        print("Failed to send metrics to Prometheus")
        sys.exit(1)

if __name__ == "__main__":
    main()