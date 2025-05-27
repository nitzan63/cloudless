from services.base_service import BaseService
import requests

class ProviderService(BaseService):
    def create_provider(self, user_id: str, public_key: str):
        payload = {
            "user_id": user_id,
            "public_key": public_key
        }
        response = requests.post(f"{self.base_url}/providers/", params=payload)
        return self._handle_response(response)

    def get_provider(self, user_id: int):
        response = requests.get(f"{self.base_url}/providers/{user_id}")
        return self._handle_response(response)

    def update_last_connection(self, provider_id: int):
        response = requests.post(f"{self.base_url}/providers/{provider_id}/touch")
        return self._handle_response(response)
