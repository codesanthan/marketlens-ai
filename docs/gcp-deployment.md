# GCP deployment

Run `PROJECT_ID=... REGION=us-central1 ./infra/gcp/setup.sh`. Configure GitHub Workload Identity
Federation as described in `docs/github-actions.md`. Submit each build from the repository root:

```sh
gcloud builds submit --config cloudbuild-api.yaml --substitutions _REGION=us-central1
gcloud builds submit --config cloudbuild-web.yaml --substitutions _REGION=us-central1,_API_URL=https://API_URL
```

The services use minimum instances zero, Artifact Registry, Cloud Logging, and Cloud Monitoring.
After deploying the API, set the web service's `API_BASE_URL` to its HTTPS URL and set the API's
`ALLOWED_ORIGINS` to the web URL. Yahoo requires outbound internet access and offers no availability
SLA. Placeholder secrets should be populated only if a future connector requires them.

