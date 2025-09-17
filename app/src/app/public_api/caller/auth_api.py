from typing import Optional, Tuple
from core.protocol import HttpClient, AuthHandler, AuthConfig
from app.src.app.public_api.constants.auth_endpoints import LOGIN_TOKEN, REFRESH_TOKEN
from app.src.app.public_api.model.auth_models import TokenPair


class AuthAPI:
    """
    公共 API：JWT 登录、刷新与将 Bearer 注入 HttpClient。
    """

    def __init__(self, client: HttpClient):
        self.client = client

    def get_token(self, username: str, password: str, number: Optional[str] = None) -> TokenPair:
        """
        调用 /api/user/get_token/ 获取 access/refresh
        请求体会包含: {"username": "...", "password": "...", "number": "...?(可选)"}
        """
        payload = {
            "username": username,
            "password": password,
        }
        if number:
            payload["number"] = number

        resp = self.client.post(LOGIN_TOKEN, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"get_token failed: {resp.status_code} {resp.text}")

        data = resp.json()
        access = data.get("access")
        refresh = data.get("refresh")
        if not access or not refresh:
            raise RuntimeError(f"get_token response missing access/refresh: {data}")

        return TokenPair(access=access, refresh=refresh)

    def refresh_token(self, refresh: str) -> str:
        """
        调用 /api/user/refresh_token/ 获取新的 access
        """
        resp = self.client.post(REFRESH_TOKEN, json={"refresh": refresh})
        if resp.status_code != 200:
            raise RuntimeError(f"refresh_token failed: {resp.status_code} {resp.text}")

        data = resp.json()
        access = data.get("access")
        if not access:
            raise RuntimeError(f"refresh_token response missing access: {data}")
        return access

    def apply_bearer(self, access: str) -> None:
        """
        将 Bearer Token 注入 HttpClient（默认头），后续请求自动带上 Authorization。
        """
        auth = AuthHandler(AuthConfig(auth_type="bearer", token=access))
        self.client.set_headers(auth.get_auth_headers())