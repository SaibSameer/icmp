# Monitoring Setup Guide

## Overview
This document outlines the monitoring setup for the ICMP Backend service, including logging, metrics collection, alerting, and visualization.

## Error Tracking Metrics

### 1. Error Count Metrics
```python
# Error tracking metrics
ERROR_COUNT = Counter(
    'icmp_errors_total',
    'Total number of errors',
    ['error_type', 'error_code']
)

ERROR_RATE = Gauge(
    'icmp_error_rate',
    'Error rate per minute',
    ['error_type']
)

ERROR_DURATION = Histogram(
    'icmp_error_duration_seconds',
    'Time between errors',
    ['error_type']
)
```

### 2. Error Details Metrics
```python
# Error details metrics
ERROR_CONTEXT = Counter(
    'icmp_error_context_total',
    'Error context occurrences',
    ['error_type', 'context_key']
)

ERROR_FIELD = Counter(
    'icmp_error_field_total',
    'Field error occurrences',
    ['error_type', 'field_name']
)

ERROR_SERVICE = Counter(
    'icmp_error_service_total',
    'Service error occurrences',
    ['service_name', 'error_type']
)
```

### 3. Error Tracking Dashboard

#### Error Overview
- Total error count
- Error rate over time
- Error type distribution
- Error severity levels
- Error resolution time

#### Error Details
- Error context analysis
- Field error patterns
- Service error breakdown
- Error correlation
- Error impact analysis

#### Error Alerts
- High error rate
- Critical errors
- Error patterns
- Service failures
- Resolution time

## Logging Setup

## 1. Application Logging

### Log Configuration
```python
# backend/config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    log_file = os.getenv('LOG_FILE', 'logs/app.log')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
```

### Log Categories
1. **Application Logs**
   - Request/Response logging
   - Error tracking
   - Performance metrics
   - Security events

2. **Database Logs**
   - Query execution
   - Connection issues
   - Performance metrics
   - Error tracking

3. **External Service Logs**
   - API calls
   - Response times
   - Error tracking
   - Rate limiting

## 2. Nginx Logging

### Access Log Configuration
```nginx
# /etc/nginx/sites-available/icmp-backend
server {
    # ... existing configuration ...
    
    access_log /var/log/nginx/icmp-backend-access.log combined buffer=512k flush=1m;
    error_log /var/log/nginx/icmp-backend-error.log warn;
}
```

### Log Rotation
```bash
# /etc/logrotate.d/icmp-backend
/var/log/nginx/icmp-backend-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### Metrics Collection

## 1. Prometheus Setup

### Installation
```bash
# Install Prometheus
sudo apt-get install -y prometheus

# Install Node Exporter
sudo apt-get install -y prometheus-node-exporter
```

### Configuration
```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'icmp-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scheme: 'http'

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### Custom Metrics
```python
# backend/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter(
    'icmp_request_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'icmp_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

# Database metrics
DB_CONNECTIONS = Gauge(
    'icmp_db_connections',
    'Number of active database connections'
)

DB_QUERY_LATENCY = Histogram(
    'icmp_db_query_latency_seconds',
    'Database query latency in seconds',
    ['query_type']
)

# Cache metrics
CACHE_HITS = Counter(
    'icmp_cache_hits_total',
    'Total number of cache hits'
)

CACHE_MISSES = Counter(
    'icmp_cache_misses_total',
    'Total number of cache misses'
)

# Template metrics
TEMPLATE_RENDER_TIME = Histogram(
    'icmp_template_render_seconds',
    'Template rendering time in seconds',
    ['template_name']
)

# Error metrics
ERROR_COUNT = Counter(
    'icmp_errors_total',
    'Total number of errors',
    ['error_type']
)
```

## 2. Grafana Setup

### Installation
```bash
# Install Grafana
sudo apt-get install -y grafana
```

### Configuration
```ini
# /etc/grafana/grafana.ini
[server]
http_port = 3000
domain = your-domain.com
root_url = https://your-domain.com/grafana

[security]
admin_user = admin
admin_password = your_secure_password

[auth.anonymous]
enabled = true
org_name = Main Org.
org_role = Viewer
```

### Dashboard Setup
1. **System Overview**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

2. **Application Metrics**
   - Request rate
   - Response time
   - Error rate
   - Cache hit ratio

3. **Database Metrics**
   - Connection pool
   - Query latency
   - Transaction rate
   - Error rate

4. **Template Metrics**
   - Render time
   - Cache hits
   - Error rate
   - Usage statistics

### Alerting Setup

## 1. Alertmanager Configuration

### Installation
```bash
# Install Alertmanager
sudo apt-get install -y prometheus-alertmanager
```

### Configuration
```yaml
# /etc/prometheus/alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/your-webhook-url'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'

receivers:
- name: 'slack-notifications'
  slack_configs:
  - channel: '#alerts'
    send_resolved: true
```

## 2. Alert Rules

### Prometheus Rules
```yaml
# /etc/prometheus/rules/icmp-backend.yml
groups:
- name: icmp-backend
  rules:
  - alert: HighErrorRate
    expr: rate(icmp_errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
      description: Error rate is above 10% for the last 5 minutes

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(icmp_request_latency_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: High latency detected
      description: 95th percentile latency is above 1 second

  - alert: DatabaseConnectionIssues
    expr: icmp_db_connections < 1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: Database connection issues
      description: No active database connections

  - alert: HighCacheMissRate
    expr: rate(icmp_cache_misses_total[5m]) / rate(icmp_cache_hits_total[5m]) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: High cache miss rate
      description: Cache miss rate is above 50%
```

### Health Checks

## 1. Application Health

### Health Check Endpoint
```python
# backend/routes/health.py
from flask import Blueprint, jsonify
from prometheus_client import generate_latest

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@health_bp.route('/metrics')
def metrics():
    return generate_latest()
```

### Health Check Script
```bash
#!/bin/bash
# /usr/local/bin/check-icmp-health.sh

# Check application health
curl -s http://localhost:8000/health | grep -q '"status":"healthy"'
if [ $? -ne 0 ]; then
    echo "Application health check failed"
    exit 1
fi

# Check database connection
psql -U icmp_user -d icmp_db -c "SELECT 1" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Database health check failed"
    exit 1
fi

# Check Redis connection
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Redis health check failed"
    exit 1
fi

echo "All health checks passed"
exit 0
```

### Performance Monitoring

## 1. Resource Monitoring

### CPU Monitoring
```bash
# /usr/local/bin/monitor-cpu.sh
#!/bin/bash

THRESHOLD=80
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')

if (( $(echo "$CPU_USAGE > $THRESHOLD" | bc -l) )); then
    echo "High CPU usage detected: $CPU_USAGE%"
    exit 1
fi
```

### Memory Monitoring
```bash
# /usr/local/bin/monitor-memory.sh
#!/bin/bash

THRESHOLD=80
MEMORY_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')

if (( $(echo "$MEMORY_USAGE > $THRESHOLD" | bc -l) )); then
    echo "High memory usage detected: $MEMORY_USAGE%"
    exit 1
fi
```

## 2. Application Performance

### Request Timing
```python
# backend/middleware/timing.py
from functools import wraps
from time import time
from .metrics import REQUEST_LATENCY

def timing_middleware():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time()
            response = f(*args, **kwargs)
            duration = time() - start_time
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.endpoint
            ).observe(duration)
            
            return response
        return wrapped
    return decorator
```

### Database Performance
```python
# backend/database/monitoring.py
from contextlib import contextmanager
from time import time
from ..monitoring.metrics import DB_QUERY_LATENCY

@contextmanager
def monitor_query(query_type):
    start_time = time()
    try:
        yield
    finally:
        duration = time() - start_time
        DB_QUERY_LATENCY.labels(query_type=query_type).observe(duration)
```

### Security Monitoring

## 1. Access Monitoring

### Authentication Logging
```python
# backend/security/monitoring.py
from .metrics import ERROR_COUNT

def log_auth_attempt(success, user_id=None):
    if not success:
        ERROR_COUNT.labels(error_type='auth_failure').inc()
        logger.warning(f"Failed authentication attempt for user: {user_id}")
```

### API Access Logging
```python
# backend/middleware/access_log.py
from .metrics import REQUEST_COUNT

def access_log_middleware():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint,
                status=response.status_code
            ).inc()
            
            return response
        return wrapped
    return decorator
```

## 2. Security Alerts

### Suspicious Activity
```yaml
# /etc/prometheus/rules/security.yml
groups:
- name: security
  rules:
  - alert: SuspiciousActivity
    expr: rate(icmp_errors_total{error_type="auth_failure"}[5m]) > 10
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: Suspicious activity detected
      description: High rate of authentication failures
```

## Maintenance

## 1. Log Rotation

### Application Logs
```bash
# /etc/logrotate.d/icmp-backend
/var/log/icmp-backend/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload icmp-backend
    endscript
}
```

## 2. Metrics Retention

### Prometheus Retention
```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  scrape_timeout: 10s
  external_labels:
    monitor: 'icmp-backend'
  storage:
    tsdb:
      retention:
        time: 15d
        size: 512MB
```

## 3. Dashboard Maintenance

### Regular Updates
1. Review and update dashboards monthly
2. Add new metrics as needed
3. Adjust alert thresholds based on historical data
4. Archive unused dashboards

### Conclusion

This monitoring setup provides comprehensive visibility into the ICMP Backend service's performance, health, and security. Regular maintenance and updates are essential for ensuring the monitoring system remains effective and relevant.

Last Updated: 2025-05-12

## Error Alert Rules
```yaml
# /etc/prometheus/rules/error_alerts.yml
groups:
  - name: error_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(icmp_errors_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High error rate detected
          description: Error rate is {{ $value }} per second

      - alert: CriticalErrors
        expr: icmp_errors_total{error_type="critical"} > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: Critical errors detected
          description: {{ $value }} critical errors in the last minute

      - alert: ServiceErrors
        expr: rate(icmp_error_service_total[5m]) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High service error rate
          description: Service error rate is {{ $value }} per second
```

## Error Notification Channels
```yaml
# /etc/prometheus/alertmanager.yml
receivers:
  - name: 'error-alerts'
    slack_configs:
      - channel: '#error-alerts'
        send_resolved: true
    email_configs:
      - to: 'team@example.com'
        send_resolved: true
```

## Best Practices

### 1. Error Monitoring
- Track all error types
- Monitor error rates
- Analyze error patterns
- Set up alerts
- Review error trends

### 2. Error Analysis
- Review error context
- Track error resolution
- Monitor error impact
- Analyze error correlation
- Update error handling

### 3. Error Reporting
- Generate error reports
- Track error metrics
- Monitor error trends
- Share error insights
- Update error handling

## Related Documentation
- See [Error Handling Guide](error_handling.md) for error handling procedures
- See [Troubleshooting Guide](troubleshooting.md) for error resolution
- See [API Documentation](api_documentation.md) for error responses
