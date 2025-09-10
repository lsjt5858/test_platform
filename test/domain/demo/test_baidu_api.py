import requests
import allure

@allure.feature("Baidu GET API")
@allure.story("Search endpoint")
@allure.title("验证百度搜索GET接口可用性与基础响应")
def test_baidu_search_get():
    # 1. 请求构造 & 参数传递
    url = "https://www.baidu.com/s"
    params = {"wd": "pytest 接口测试"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }

    with allure.step("发送GET请求"):
        resp = requests.get(url, params=params, headers=headers, timeout=10)

    # 2. 响应接收 & 断言
    with allure.step("基础断言与字段校验"):
        assert resp.status_code == 200
        assert "百度" in resp.text
        allure.attach(str(resp.status_code), name="status_code", attachment_type=allure.attachment_type.TEXT)
        allure.attach(resp.url, name="final_url", attachment_type=allure.attachment_type.TEXT)
        allure.attach(resp.text[:1000], name="body_snippet", attachment_type=allure.attachment_type.TEXT)