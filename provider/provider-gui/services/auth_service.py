from services.base_service import BaseService
import requests

class AuthService(BaseService):
    def __init__(self, base_url):
        super().__init__(base_url)

    def register(self, username, password):
        url = f"{self.base_url}/register"
        payload = {"username": username, "password": password, "type": "provider"}
        response = requests.post(url, json=payload)
        return self._handle_response(response)

    def login(self, username, password):
        url = f"{self.base_url}/login"
        payload = {"username": username, "password": password}
        # The FastAPI login endpoint expects form data, not JSON
        data = {"username": username, "password": password}
        response = requests.post(url, data=data)
        return self._handle_response(response) 