
class BaseService:
    def __init__(self, base_url: str = ''):
        self.base_url = base_url

    def _handle_response(self, response):
        response.raise_for_status()
        return response.json()
