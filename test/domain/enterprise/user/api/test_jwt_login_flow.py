# import pytest
#
# from core.protocol import HttpClient
# from app.public_api.caller.auth_api import AuthAPI
#
#
# @pytest.mark.integration
# def test_jwt_login_and_refresh(http_client: HttpClient):
#     """
#     基于当前框架串联一条 JWT 登录 + 刷新用例：
#     1) /api/user/get_token/ -> 获取 access/refresh
#     2) 将 access 设置为默认 Authorization: Bearer
#     3) /api/user/refresh_token/ -> 刷新出新的 access
#     """
#     # 你给的登录入参
#     number = "001"
#     username = "admin"
#     password = "Lx123456"
#
#     api = AuthAPI(http_client)
#
#     # 1) 登录获取 token
#     pair = api.get_token(username=username, password=password, number=number)
#     assert pair.access and pair.refresh
#
#     # 2) 应用 Bearer 头到 http_client（后续请求自动携带 Authorization）
#     api.apply_bearer(pair.access)
#     # 断言默认头部已经包含 Authorization
#     assert "Authorization" in http_client.session.headers
#     assert http_client.session.headers["Authorization"].startswith("Bearer ")
#
#     # 3) 刷新 access
#     new_access = api.refresh_token(pair.refresh)
#     assert new_access and new_access != pair.access