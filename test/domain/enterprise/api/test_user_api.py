import pytest
from biz.enterprise.biz_ops.user_flow import UserFlow

@pytest.fixture
def user_flow():
    return UserFlow(env="test")

def test_user_login_and_order(user_flow):
    order_id = user_flow.login_and_create_order(
        user_id=123,
        order_data={"product": "book", "quantity": 1}
    )
    assert order_id is not None
    print(f"✅ Order created: {order_id}")
    print("🎉 Test passed.")