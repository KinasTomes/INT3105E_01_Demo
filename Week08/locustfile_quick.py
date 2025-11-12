"""
Locust Quick Load Test - Read-heavy operations
Optimized for fast validation with mostly read operations
"""

from locust import HttpUser, task, between
import random


class QuickLoadTest(HttpUser):
    """Quick load test - mostly read operations"""
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Login on start"""
        response = self.client.post(
            "/auth/login",
            json={"username": "user", "password": "user123"},
            name="Login"
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"✓ User logged in successfully")
        else:
            self.headers = {}
            print(f"✗ Login failed: {response.status_code}")
    
    @task(10)
    def list_products(self):
        """List products - 50% of traffic"""
        params = {"skip": 0, "limit": 20}
        self.client.get("/products", params=params, headers=self.headers, name="List Products")
    
    @task(5)
    def get_product(self):
        """Get specific product - 25% of traffic"""
        product_id = random.randint(1, 50)
        self.client.get(
            f"/products/{product_id}", 
            headers=self.headers, 
            name="Get Product",
            catch_response=True
        )
    
    @task(1)
    def create_product(self):
        """Create product - 5% of traffic"""
        self.client.post(
            "/products",
            json={
                "name": f"Quick_Product_{random.randint(1, 9999)}",
                "price": round(random.uniform(10, 500), 2),
                "stock": random.randint(1, 50),
                "description": "Quick test product"
            },
            headers=self.headers,
            name="Create Product"
        )
