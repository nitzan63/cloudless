from abc import ABC, abstractmethod
from typing import Any

class StorageService(ABC):
    @abstractmethod
    def upload_file(self, file_content: Any, filename: str) -> dict:
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> dict:
        pass

    @abstractmethod
    def get_file(self, file_path: str) -> dict:
        """Retrieve file content"""
        pass
