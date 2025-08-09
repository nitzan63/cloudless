from services.storage.local_storage import LocalStorageService
from services.storage.google_storage import GoogleStorageService
import os

# Choose storage backend via env var: 'local' (default) or 'gcs'
_BACKEND = os.getenv('STORAGE_BACKEND', 'local').lower()

if _BACKEND == 'gcs':
    storage_service = GoogleStorageService()
else:
    storage_service = LocalStorageService()  # default