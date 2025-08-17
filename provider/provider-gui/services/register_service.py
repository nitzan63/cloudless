from services.base_service import BaseService
from services.secrets_service import SecretsService
import requests

class RegisterService(BaseService):
    def __init__(self, base_url, secrets_service: SecretsService):
        super().__init__(base_url)
        self.secrets_service = secrets_service

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.secrets_service.get_token()}"
        }

    def register(self):
        url = f"{self.base_url}/register"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)

    def get_details(self):
        url = f"{self.base_url}/details"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)

    def trigger(self):
        url = f"{self.base_url}/trigger"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
