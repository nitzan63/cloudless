# Google Cloud Storage Integration Guide

This project supports Google Cloud Storage (GCS) for storing scripts, datasets, and results.

Follow these steps to set up credentials, buckets, and environment variables for both local development and cloud deployment.

## 1) Create a GCS Bucket
- Console path: Storage → Buckets → Create
- Choose a bucket name (e.g., `cloudless-files`), region close to your compute.
- Choose Standard storage class.
- Access control: Uniform bucket-level access (recommended).
- Click Create.

## 2) Create a Service Account (SA)
- Console path: IAM & Admin → Service Accounts → Create service account.
- Name: `cloudless-data-service`
- Click Create and continue.
- Grant roles:
  - Storage Object Admin: `roles/storage.objectAdmin`
  - (Optional, for keyless signed URLs): Service Account Token Creator: `roles/iam.serviceAccountTokenCreator`
- Click Continue → Done.

If you deploy on GKE/Cloud Run/GCE with the attached service account and grant `roles/iam.serviceAccountTokenCreator`, the `google-cloud-storage` client can generate signed URLs without a JSON key (V4 signing with IAM).

## 3) Credentials: Local vs Cloud

- Local development (JSON key file):
  - Console: IAM & Admin → Service Accounts → `cloudless-data-service` → Keys → Add Key → Create new key → JSON → Download.
  - Save to: `~/.gcp/cloudless-data-service-key.json`.

- Cloud deployment (no keys):
  - Attach the service account to your runtime (GKE/Cloud Run/GCE).
  - Ensure the workload identity/attached SA is `cloudless-data-service` and has the roles above.

## 4) Environment Variables

Data Service selects the storage backend via env:
- `STORAGE_BACKEND=gcs`
- `GCS_BUCKET_NAME=<your-bucket-name>`
- Local only: `GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json`

Example docker-compose snippet (local):

```
services:
  data-service:
    environment:
      - PORT=8002
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypassword
      - POSTGRES_DB=mydatabase
      - POSTGRES_PORT=5432
      - POSTGRES_HOST=db
      - STORAGE_BACKEND=gcs
      - GCS_BUCKET_NAME=cloudless-files
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    volumes:
      - ~/.gcp/cloudless-data-service-key.json:/secrets/gcp-key.json:ro
```

Executors and other services do not need GCS credentials; they download via signed URLs from the Data Service.

## 5) What changed in code (high level)
- Data Service now supports GCS (selected via `STORAGE_BACKEND`).
- Upload API stores scripts and optional dataset in GCS.
- Executors fetch script (and dataset if provided) via short-lived signed URLs.
- Results will be exposed via `results_path` and proxied through the main server (`/api/tasks/<id>/results`).

## 6) Writing Spark jobs to use datasets and write results
- Spark script receives dataset URL as the first argument (if provided).
- Read dataset in your script, e.g.:

```python
import sys
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MyJob").getOrCreate()

# Optional dataset URL passed as first arg
dataset_url = sys.argv[1] if len(sys.argv) > 1 else None
if dataset_url:
    df = spark.read.option("header", True).csv(dataset_url)
    # process ...

# When done, write results locally, then upload via the Data Service upload endpoint from the executor or the script.
# Update the task's results_path via the data-service PATCH API.

spark.stop()
```

Two options to store results to GCS:
- Option A (recommended): executor uploads generated result files via Data Service `/storage/upload`, then updates task with `results_path` using `/tasks/{id}` PATCH.
- Option B: have the script write directly to GCS using `google-cloud-storage` (requires providing credentials in the job; not recommended initially).

## 7) UI: submitting a dataset
- The UI now supports attaching an optional dataset file, which is uploaded and stored in GCS.
- A "Download Results" button appears per task when `results_path` is set.

## 8) Troubleshooting
- Permission denied: Verify the SA roles and bucket name.
- Signed URL generation errors: ensure SA has `roles/iam.serviceAccountTokenCreator` or that `GOOGLE_APPLICATION_CREDENTIALS` is set locally.
- 404 on `/storage/get-file`: confirm `STORAGE_BACKEND` and bucket/paths, and that the Data Service is reachable.

## 9) Security best practices
- Prefer Workload Identity / attached service accounts in cloud (no JSON keys).
- Keep key files outside source control; mount as read-only.
- Short signed URL expiry (default 10 minutes).
- Use clear prefixes: `uploads/` (scripts), `datasets/`, `results/`. 