from google.cloud import storage
import os
from datetime import datetime
from .storage_service import StorageService

class GoogleStorageService(StorageService):
    def __init__(self):
        # This will automatically use the default credentials
        # When running on GCP, it will use the service account attached to the instance
        self.client = storage.Client()
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'cloudless-files')
        self.bucket = self.client.bucket(self.bucket_name)
        self.bucket.reload()

    def upload_file(self, file_content, filename):
        """Upload any file to GCS"""
        try:
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f'uploads/{timestamp}_{filename}'
            
            # Create blob and upload
            blob = self.bucket.blob(unique_filename)
            blob.upload_from_string(file_content)
            
            return {
                'status': 'success',
                'file_path': unique_filename,
                'public_url': blob.public_url
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def delete_file(self, file_path):
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