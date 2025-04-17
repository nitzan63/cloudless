from abc import ABC, abstractmethod

class StorageService(ABC):
    @abstractmethod
    def upload_file(self, file_content, filename):
        pass
            
    @abstractmethod
    def delete_file(self, file_path):
        pass
