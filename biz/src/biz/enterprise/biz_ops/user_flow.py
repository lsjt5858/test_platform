from app.enterprise.caller.enterprise_client import EnterpriseClient
from core.pytest_util.assertions import CustomAssertions

class UserFlow:
    def __init__(self, env="default"):
        self.client = EnterpriseClient(env)
        self.assertions = CustomAssertions()

    def login_and_create_order(self, user_id, order_data):
        # Step 1: 获取用户信息
        user_resp = self.client.get_user_info(user_id)
        self.assertions.assert_status_code(user_resp)

        # Step 2: 创建订单
        order_resp = self.client.create_order(order_data)
        self.assertions.assert_status_code(order_resp)
        self.assertions.assert_json_key(order_resp, "order_id")

        return order_resp.json()["order_id"]