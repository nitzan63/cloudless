import os
from datetime import datetime
from services.storage.storage_service import StorageService
from typing import Any

class LocalStorageService(StorageService):
    def __init__(self):
        # Use an env var or default to `local-storage`
        self.base_path = os.getenv('LOCAL_STORAGE_PATH', 'server/local-storage')
        self.uploads_path = os.path.join(self.base_path, 'uploads')
        os.makedirs(self.uploads_path, exist_ok=True)

    def upload_file(self, file_content: Any, filename: str) -> dict:
        """Upload any file to local storage"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f'{timestamp}_{filename}'
            full_path = os.path.join(self.uploads_path, unique_filename)

            with open(full_path, 'wb') as f:
                f.write(file_content)

            return {
                'status': 'success',
                'file_path': os.path.relpath(full_path, start=self.base_path),
                'absolute_path': os.path.abspath(full_path),
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def delete_file(self, file_path: str) -> dict:
        """Delete a file from local storage"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            os.remove(full_path)
            return {
                'status': 'success',
                'message': f'File {file_path} deleted successfully'
            }
        except FileNotFoundError:
            return {
                'status': 'error',
                'message': f'File not found: {file_path}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
