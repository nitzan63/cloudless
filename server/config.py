from services.storage.storage_service import StorageService
from services.storage.local_storage_service import LocalStorageService
from services.storage.google_storage_service import GoogleStorageService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_storage() -> StorageService:
    storage = LocalStorageService()
    try:
        storage = GoogleStorageService()
        logger.info("Connected to google cloud storage")
    except:
        logger.info("Connected to local storage")
        pass
    return storage
