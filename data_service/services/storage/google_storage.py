from google.cloud import storage
import os
from datetime import datetime, timedelta
from services.storage.storage_service import StorageService
from typing import Any

class GoogleStorageService(StorageService):
    def __init__(self):
        # This will automatically use the default credentials
        # When running on GCP, it will use the service account attached to the instance
        self.client = storage.Client()
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'cloudless-files')
        self.bucket = self.client.bucket(self.bucket_name)
        self.bucket.reload()

    def upload_file(self, file_content: Any, filename: str) -> dict:
        """Upload any file to GCS"""
        try:
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # Support dataset vs script by simple heuristic
            prefix = 'datasets' if not filename.endswith('.py') else 'uploads'
            unique_filename = f'{prefix}/{timestamp}_{filename}'
            
            # Create blob and upload
            blob = self.bucket.blob(unique_filename)
            blob.upload_from_string(file_content)
            
            return {
                'status': 'success',
                'file_path': unique_filename,
                'file_name': os.path.basename(unique_filename),
                'public_url': blob.public_url
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_file(self, file_path: str) -> dict:
        """Retrieve a file from GCS"""
        try:
            blob = self.bucket.blob(file_path)
            content = blob.download_as_bytes()
            return {
                'status': 'success',
                'file_content': content,
                'file_name': os.path.basename(file_path)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def delete_file(self, file_path: str) -> dict:
        """Delete a file from GCS"""
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            return {
                'status': 'success',
                'message': f'File {file_path} deleted successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def generate_download_url(self, file_path: str, expires_seconds: int = 600) -> str:
        blob = self.bucket.blob(file_path)
        url = blob.generate_signed_url(expiration=timedelta(seconds=expires_seconds), method="GET")
        return url 