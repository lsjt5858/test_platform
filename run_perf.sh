#!/bin/bash

# Performance Testing Script with K6 + Prometheus + Grafana
# Usage: ./run_perf.sh

set -e

echo "=€ Starting performance monitoring stack..."

# Start monitoring services
echo "=Ê Starting Prometheus, Grafana, and Pushgateway..."
docker-compose up -d prometheus grafana pushgateway

# Wait for services to be ready
echo "ó Waiting for services to start..."
sleep 5

# Check if services are healthy
echo "= Checking service health..."
if curl -s http://localhost:9090/api/v1/targets >/dev/null; then
    echo " Prometheus is running at http://localhost:9090"
else
    echo "L Prometheus failed to start"
    exit 1
fi

if curl -s http://localhost:3000/api/health >/dev/null; then
    echo " Grafana is running at http://localhost:3000 (admin/admin)"
else
    echo "L Grafana failed to start"
    exit 1
fi

if curl -s http://localhost:9091/metrics >/dev/null; then
    echo " Pushgateway is running at http://localhost:9091"
else
    echo "L Pushgateway failed to start"
    exit 1
fi

# Run K6 performance test
echo ""
echo "=% Running K6 performance test..."
docker-compose run --rm k6

# Push K6 metrics to Prometheus via Pushgateway
echo ""
echo "=ä Pushing K6 metrics to Prometheus..."
docker-compose run --rm k6-bridge

# Verify metrics are available
echo ""
echo "= Verifying K6 metrics in Prometheus..."
METRICS_COUNT=$(curl -s "http://localhost:9090/api/v1/label/__name__/values" | grep -o "k6_" | wc -l || echo "0")

if [ "$METRICS_COUNT" -gt 0 ]; then
    echo " Found $METRICS_COUNT K6 metric types in Prometheus"
    echo ""
    echo "<¯ Available K6 metrics:"
    curl -s "http://localhost:9090/api/v1/label/__name__/values" | grep -o '"k6_[^"]*"' | sort || echo "No K6 metrics found"
    
    echo ""
    echo "=Ê Sample K6 HTTP request metrics:"
    curl -s "http://localhost:9090/api/v1/query?query=k6_http_reqs" | python3 -m json.tool 2>/dev/null || echo "Could not format JSON"
else
    echo "L No K6 metrics found in Prometheus"
    exit 1
fi

echo ""
echo "<‰ Performance monitoring setup complete!"
echo ""
echo "= Access URLs:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana:    http://localhost:3000 (admin/admin)"
echo "   Pushgateway: http://localhost:9091"
echo ""
echo "=Ý To create Grafana dashboards:"
echo "   1. Open Grafana at http://localhost:3000"
echo "   2. Use data source: Prometheus (http://prometheus:9090)"
echo "   3. Query K6 metrics like: k6_http_req_duration, k6_http_reqs, k6_vus"
echo ""
echo "= To run another test:"
echo "   ./run_perf.sh"
echo ""