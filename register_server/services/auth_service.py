from services.base_service import BaseService
import requests

class AuthService(BaseService):
    def __init__(self, auth_service_url):
        super().__init__(auth_service_url)
        self.auth_service_url = auth_service_url

    def validate_token(self, token: str):
        resp = requests.get(f"{self.auth_service_url}/protected-provider", headers={"Authorization": f"Bearer {token}"})
        if resp.status_code != 200:
            return None
        return self._handle_response(resp)