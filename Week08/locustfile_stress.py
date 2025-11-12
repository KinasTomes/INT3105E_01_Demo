"""
Locust Stress Test - Aggressive concurrent requests
Tests system under heavy load with minimal wait time
"""

from locust import HttpUser, task, between
import random


class StressTest(HttpUser):
    """Stress test - aggressive concurrent requests"""
    wait_time = between(0.1, 0.5)  # Very short wait time
    
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
            print(f"✓ Stress test user logged in")
        else:
            self.headers = {}
            print(f"✗ Login failed: {response.status_code}")
    
    @task(20)
    def rapid_list(self):
        """Rapid list requests - 50% of traffic"""
        params = {"skip": random.randint(0, 10), "limit": 10}
        self.client.get("/products", params=params, headers=self.headers, name="Rapid List")
    
    @task(10)
    def rapid_get(self):
        """Rapid get requests - 25% of traffic"""
        product_id = random.randint(1, 100)
        self.client.get(
            f"/products/{product_id}", 
            headers=self.headers, 
            name="Rapid Get",
            catch_response=True
        )
    
    @task(5)
    def rapid_create(self):
        """Rapid create requests - 12.5% of traffic"""
        self.client.post(
            "/products",
            json={
                "name": f"Stress_{random.randint(1, 99999)}",
                "price": random.randint(1, 1000),
                "stock": random.randint(1, 100),
                "description": f"Stress test product {random.randint(1, 1000)}"
            },
            headers=self.headers,
            name="Rapid Create"
        )
    
    @task(3)
    def rapid_update(self):
        """Rapid update requests - 7.5% of traffic"""
        product_id = random.randint(1, 50)
        self.client.patch(
            f"/products/{product_id}",
            json={
                "price": round(random.uniform(10, 1000), 2),
                "stock": random.randint(1, 100)
            },
            headers=self.headers,
            name="Rapid Update",
            catch_response=True
        )
    
    @task(2)
    def rapid_delete(self):
        """Rapid delete requests - 5% of traffic"""
        product_id = random.randint(50, 100)
        self.client.delete(
            f"/products/{product_id}",
            headers=self.headers,
            name="Rapid Delete",
            catch_response=True
        )
