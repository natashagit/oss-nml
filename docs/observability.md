# Observability

The AI Ticket service exposes Prometheus metrics at `/metrics` via
`prometheus_fastapi_instrumentator`. These metrics back the Grafana dashboards
used for latency, success rate, and error rate visibility.

Telemetry dashboard:
http://3.239.197.228:3000/d/adbqk72/ai-ticket-service-telemetry?orgId=1
