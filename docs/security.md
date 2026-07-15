# Security

The frontend receives no connector credentials. Secrets belong in Secret Manager and Cloud Run
runtime configuration, never `NEXT_PUBLIC_*` values. The API allowlists ticker symbols, constrains
periods, caps request/correlation IDs, configures specific CORS origins, uses timeouts/retries, and
logs event metadata rather than external payloads. Containers run as non-root users. Production
operators should restrict API ingress to the web service or add authenticated service-to-service
access, set explicit Cloud Run resource limits, enable vulnerability scanning, and monitor errors.

