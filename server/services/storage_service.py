from services.base_service import BaseService
import requests

class StorageService(BaseService):
    def upload_file(self, file):
        files = {
            'file': (file.filename, file.stream, file.mimetype)
        }
        response = requests.post(f"{self.base_url}/storage/upload", files=files)
        return self._handle_response(response)

    def get_file(self, file_path: str, output_path: str):
        response = requests.get(f"{self.base_url}/storage/get-file", params={"file_path": file_path})
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return {"status": "success", "saved_to": output_path}

    def delete_file(self, file_path: str):
        response = requests.delete(f"{self.base_url}/storage/delete", data={"file_path": file_path})
        return self._handle_response(response)
