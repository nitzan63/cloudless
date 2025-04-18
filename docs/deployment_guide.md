# Deployment Guide for Cloudless Server

This guide explains how to build, push, and deploy the Cloudless server to Google Cloud Run.

## Prerequisites

1. Docker installed and running locally
2. Docker Hub account (in this case: `nitzan63`)
3. Google Cloud CLI installed and configured
4. Access to Google Cloud project with required permissions
5. Service account with necessary permissions (`cloudless-sa`)

## Build and Push Docker Image

### 1. Build the Docker Image
Navigate to the server directory and build the image:
```bash
cd server
docker build -t nitzan63/cloudless:latest .
```

The format is: `docker build -t [DOCKER_HUB_USERNAME]/[REPOSITORY_NAME]:[TAG] .`

### 2. Push to Docker Hub
Push the built image to Docker Hub:
```bash
docker push nitzan63/cloudless:latest
```

Note: Make sure you're logged in to Docker Hub (`docker login`) before pushing.

## Deploy to Cloud Run

### 1. Deploy the Image
Deploy the pushed image to Cloud Run:
```bash
gcloud run deploy cloudless-server \
  --image nitzan63/cloudless:latest \
  --region us-central1 \
  --platform managed \
  --service-account cloudless-sa@beaming-grid-456915-s6.iam.gserviceaccount.com
```

This command:
- Creates/updates a Cloud Run service named `cloudless-server`
- Uses the specified Docker image
- Deploys in the `us-central1` region
- Uses the specified service account for GCP authentication

### 2. Verify Deployment
After deployment, you'll receive a Service URL. You can test it using:
```bash
# Test health endpoint
curl https://[YOUR-SERVICE-URL]/health

# Test file upload
curl -X POST -F "file=@requirements.txt" "https://[YOUR-SERVICE-URL]/api/upload"
```

## Version Management

Instead of using `latest`, you can use specific version tags:

1. Build with version:
```bash
docker build -t nitzan63/cloudless:1.1 .
```

2. Push with version:
```bash
docker push nitzan63/cloudless:1.1
```

3. Deploy specific version:
```bash
gcloud run deploy cloudless-server \
  --image nitzan63/cloudless:1.1 \
  --region us-central1 \
  --platform managed \
  --service-account cloudless-sa@beaming-grid-456915-s6.iam.gserviceaccount.com
```

## Troubleshooting

### View Logs
To view Cloud Run service logs:
```bash
gcloud run services logs read cloudless-server --region us-central1
```

### Check Service Status
To check the current status of your service:
```bash
gcloud run services describe cloudless-server --region us-central1
```

### Common Issues
1. **Image Pull Error**: Make sure the image exists on Docker Hub and is public
2. **Permission Error**: Verify the service account has necessary permissions
3. **Port Issues**: Ensure the container listens on port 8080 (Cloud Run requirement)

## Security Notes

1. Always use specific service accounts with minimal required permissions
2. Consider using private container registry for production deployments
3. Regularly update dependencies and base images
4. Use secrets management for sensitive information 