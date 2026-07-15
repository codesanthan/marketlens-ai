# GitHub Actions deployment

CI runs on pull requests. For deployment, create a Workload Identity Pool and GitHub OIDC provider
restricted to this repository; grant its deployer service account Artifact Registry Writer, Cloud
Run Admin, Service Account User only on the runtime accounts, and Cloud Build Editor if using build
submissions. Store project ID, provider resource name, and service account email as GitHub variables.
Use `google-github-actions/auth` with `workload_identity_provider`; never create or store a JSON key.
Then authenticate Docker, build/push each image, and deploy each service using the matching runtime
service account. Protect the production environment with branch and review rules.

