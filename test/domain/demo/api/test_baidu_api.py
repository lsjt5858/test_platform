import pytest
import requests
from requests import RequestException

BASE_URL = "https://www.baidu.com"

REQUEST_CONFIG = {
    "method": "GET",
    "path": "/",
    "headers": {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "close",
    },
    "params": {},
    "timeout": 8,  # seconds
}


def _build_url(base: str, path: str) -> str:
    if not base.endswith("/") and not path.startswith("/"):
        return f"{base}/{path}"
    if base.endswith("/") and path.startswith("/"):
        return base[:-1] + path
    return base + path


def _perform_request(cfg: dict) -> requests.Response:
    url = _build_url(BASE_URL, cfg.get("path", "/"))
    try:
        resp = requests.request(
            method=cfg.get("method", "GET"),
            url=url,
            headers=cfg.get("headers") or {},
            params=cfg.get("params") or {},
            timeout=cfg.get("timeout", 8),
        )
        return resp
    except RequestException as e:
        pytest.fail(f"请求发送失败: {e}")


def _assert_basic_response(resp: requests.Response):
    # 状态码校验
    assert resp.status_code == 200, f"预期状态码 200，实际为 {resp.status_code}"

    # 响应头与类型
    ctype = resp.headers.get("Content-Type", "").lower()
    assert "text/html" in ctype, f"预期 Content-Type 包含 text/html，实际为 {ctype}"

    # 处理编码并校验内容关键字
    if not resp.encoding:
        # 使用 requests 的推断编码
        try:
            resp.encoding = resp.apparent_encoding  # type: ignore[attr-defined]
        except Exception:
            resp.encoding = "utf-8"

    text = resp.text or ""
    assert ("百度一下" in text) or ("Baidu" in text), "页面内容中未发现预期关键字"

    # 响应时间（非强约束，给出合理上限）
    elapsed_ms = resp.elapsed.total_seconds() * 1000.0
    assert elapsed_ms < 5000, f"响应时间过长: {elapsed_ms:.0f}ms"


@pytest.mark.api
@pytest.mark.smoke
def test_baidu_homepage_accessible():
    """
    用例名称: 访问百度首页
    测试目标: 验证百度首页可达，返回 200 且为 HTML 页面，并包含关键字
    前置条件: 可访问公网
    步骤:
      1. 使用 GET 请求访问 https://www.baidu.com/
      2. 校验状态码、Content-Type 与页面关键字
    预期:
      - 状态码为 200
      - Content-Type 包含 text/html
      - 页面包含“百度一下”或“Baidu”关键字
    异常处理:
      - 网络异常/超时等会在发送阶段被捕获并以失败信息抛出
    """
    resp = _perform_request(REQUEST_CONFIG)
    _assert_basic_response(resp)