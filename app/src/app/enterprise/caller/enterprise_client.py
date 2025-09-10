from core.protocol.http_client import HttpClient

class EnterpriseClient:
    def __init__(self, env="default"):
        self.client = HttpClient(env=env)

    def get_user_info(self, user_id):
        return self.client.get(f"/api/v1/users/{user_id}")

    def create_order(self, data):
        return self.client.post("/api/v1/orders", json=data)

    def get_order_info(self, order_id):
        return self.client.get(f"/api/v1/orders/{order_id}")

    def update_order(self, order_id, data):
        return self.client.put(f"/api/v1/orders/{order_id}", json=data)

    def delete_order(self, order_id):
        return self.client.delete(f"/api/v1/orders/{order_id}")