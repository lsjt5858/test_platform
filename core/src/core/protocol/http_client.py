import requests
from core.config.config_loader import ConfigLoader

class HttpClient:
    def __init__(self, base_url=None, env="default"):
        self.config = ConfigLoader(env)
        self.base_url = base_url or self.config.get("API", "base_url")
        self.session = requests.Session()

    def get(self, path, **kwargs):
        return self.session.get(self.base_url + path, **kwargs)

    def post(self, path, **kwargs):
        return self.session.post(self.base_url + path, **kwargs)

    def put(self, path, **kwargs):
        return self.session.put(self.base_url + path, **kwargs)

    def delete(self, path, **kwargs):
        return self.session.delete(self.base_url + path, **kwargs)

    def patch(self, path, **kwargs):
        return self.session.patch(self.base_url + path, **kwargs)

    def options(self, path, **kwargs):
        return self.session.options(self.base_url + path, **kwargs)

    def head(self, path, **kwargs):
        return self.session.head(self.base_url + path, **kwargs)