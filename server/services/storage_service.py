from google.cloud import storage
import os
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        # This will automatically use the default credentials
        # When running on GCP, it will use the service account attached to the instance
        self.client = storage.Client()
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'cloudless-files')
        self.bucket = self.client.bucket(self.bucket_name)

    def get_upload_url(self, filename: str, expiration_minutes: int = 15) -> dict:
        """
        Generate a signed URL for uploading a file directly to GCS.
        
        Args:
            filename: Name of the file to upload
            expiration_minutes: How long the URL is valid for
            
        Returns:
            dict: Contains the upload URL and the file path
        """
        try:
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f'uploads/{timestamp}_{filename}'
            
            # Create blob
            blob = self.bucket.blob(unique_filename)
            
            # Generate signed URL for upload
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.now() + timedelta(minutes=expiration_minutes),
                method="PUT",
                content_type="application/octet-stream"
            )
            
            return {
                'status': 'success',
                'url': url,
                'file_path': unique_filename
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def download_file(self, file_path: str) -> str:
        """
        Download a file from GCS and return its content.
        
        Args:
            file_path: Path to the file in GCS
            
        Returns:
            str: Content of the file
        """
        try:
            blob = self.bucket.blob(file_path)
            return blob.download_as_text()
        except Exception as e:
            logger.error(f"Error downloading file {file_path}: {str(e)}")
            return None

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