# Security

The frontend receives no connector credentials. Secrets belong in Secret Manager and Cloud Run
runtime configuration, never `NEXT_PUBLIC_*` values. The API validates ticker symbol format, constrains
periods, caps request/correlation IDs, configures specific CORS origins, uses timeouts/retries, and
logs event metadata rather than external payloads. Containers run as non-root users. Production
SEC access must identify the application with a monitored contact address in `SEC_USER_AGENT` and
must retain conservative caching and request rates.
operators should restrict API ingress to the web service or add authenticated service-to-service
access, set explicit Cloud Run resource limits, enable vulnerability scanning, and monitor errors.
