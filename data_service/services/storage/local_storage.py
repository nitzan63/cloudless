import os
from datetime import datetime
from services.storage.storage_service import StorageService
from typing import Any

class LocalStorageService(StorageService):
    def __init__(self):
        # Use an env var or default to `local-storage`
        self.base_path = os.path.join(os.path.dirname(__file__), 'local-storage')
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
                'file_path': full_path,
                'file_name': unique_filename,
                'absolute_path': os.path.abspath(full_path),
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_file(self, file_path: str) -> dict:
        """Retrieve a file from local storage"""
        try:
            print("here 1")
            full_path = os.path.join(self.base_path, file_path)
            print(file_path)
            with open(full_path, 'rb') as f:
                return {
                    'status': 'success',
                    'file_content': f.read(),
                    'file_name': os.path.basename(file_path)
                }
            print("here 2")
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
