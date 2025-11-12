"""
Locust Load Testing Script for Products API
Run with: locust -f locustfile.py --host=http://localhost:8080
"""

from locust import HttpUser, task, between, SequentialTaskSet
import random
import json


class UserBehavior(SequentialTaskSet):
    """Sequential tasks simulating real user behavior"""
    
    def on_start(self):
        """Called when a simulated user starts - login to get token"""
        self.login()
        self.product_ids = []
    
    def login(self):
        """Login to get access token"""
        response = self.client.post(
            "/auth/login",
            json={
                "username": "user",
                "password": "user123"
            },
            headers={"Content-Type": "application/json"},
            name="Login"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            print(f"✓ Login successful, token obtained")
        else:
            print(f"✗ Login failed: {response.status_code}")
            self.token = ""
            self.headers = {"Content-Type": "application/json"}
    
    @task(1)
    def create_product(self):
        """Create a new product"""
        product_data = {
            "name": f"Product_{random.randint(1000, 9999)}",
            "price": round(random.uniform(10, 1000), 2),
            "stock": random.randint(1, 100),
            "description": f"Test product description {random.randint(1, 100)}"
        }
        
        response = self.client.post(
            "/products",
            json=product_data,
            headers=self.headers,
            name="Create Product"
        )
        
        if response.status_code == 200 or response.status_code == 201:
            product = response.json()
            if "id" in product:
                self.product_ids.append(product["id"])
                print(f"✓ Created product ID: {product['id']}")
    
    @task(5)
    def get_product(self):
        """Get a specific product by ID"""
        if self.product_ids:
            product_id = random.choice(self.product_ids)
            self.client.get(
                f"/products/{product_id}",
                headers=self.headers,
                name="Get Product by ID"
            )
        else:
            # Try a random ID if no products created yet
            self.client.get(
                f"/products/{random.randint(1, 100)}",
                headers=self.headers,
                name="Get Product by ID",
                catch_response=True
            )
    
    @task(3)
    def list_products(self):
        """List all products with pagination"""
        params = {
            "skip": random.randint(0, 10),
            "limit": random.randint(5, 20)
        }
        self.client.get(
            "/products",
            params=params,
            headers=self.headers,
            name="List Products"
        )
    
    @task(2)
    def update_product(self):
        """Update an existing product"""
        if self.product_ids:
            product_id = random.choice(self.product_ids)
            update_data = {
                "name": f"Updated_Product_{random.randint(1000, 9999)}",
                "price": round(random.uniform(10, 1000), 2),
                "stock": random.randint(1, 100),
                "description": "Updated description"
            }
            
            self.client.put(
                f"/products/{product_id}",
                json=update_data,
                headers=self.headers,
                name="Update Product (PUT)"
            )
    
    @task(2)
    def partial_update_product(self):
        """Partially update an existing product"""
        if self.product_ids:
            product_id = random.choice(self.product_ids)
            update_data = {
                "price": round(random.uniform(10, 1000), 2),
                "stock": random.randint(1, 100)
            }
            
            self.client.patch(
                f"/products/{product_id}",
                json=update_data,
                headers=self.headers,
                name="Update Product (PATCH)"
            )
    
    @task(1)
    def delete_product(self):
        """Delete a product"""
        if len(self.product_ids) > 3:  # Keep at least 3 products
            product_id = self.product_ids.pop(random.randint(0, len(self.product_ids) - 1))
            self.client.delete(
                f"/products/{product_id}",
                headers=self.headers,
                name="Delete Product"
            )
            print(f"✓ Deleted product ID: {product_id}")


class WebsiteUser(HttpUser):
    """Simulated user class"""
    tasks = [UserBehavior]
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    # You can set a fixed host here instead of using --host flag
    # host = "http://localhost:8080"


class QuickLoadTest(HttpUser):
    """Quick load test - mostly read operations"""
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Login on start"""
        response = self.client.post(
            "/auth/login",
            json={"username": "user", "password": "user123"}
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(10)
    def list_products(self):
        self.client.get("/products", headers=self.headers)
    
    @task(5)
    def get_product(self):
        product_id = random.randint(1, 50)
        self.client.get(f"/products/{product_id}", headers=self.headers, catch_response=True)
    
    @task(1)
    def create_product(self):
        self.client.post(
            "/products",
            json={
                "name": f"Quick_Product_{random.randint(1, 9999)}",
                "price": 99.99,
                "stock": 10,
                "description": "Quick test"
            },
            headers=self.headers
        )


class StressTest(HttpUser):
    """Stress test - aggressive concurrent requests"""
    wait_time = between(0.1, 0.5)  # Very short wait time
    
    def on_start(self):
        response = self.client.post(
            "/auth/login",
            json={"username": "user", "password": "user123"}
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(20)
    def rapid_list(self):
        self.client.get("/products", headers=self.headers)
    
    @task(10)
    def rapid_get(self):
        product_id = random.randint(1, 100)
        self.client.get(f"/products/{product_id}", headers=self.headers, catch_response=True)
    
    @task(5)
    def rapid_create(self):
        self.client.post(
            "/products",
            json={
                "name": f"Stress_{random.randint(1, 99999)}",
                "price": random.randint(1, 1000),
                "stock": random.randint(1, 100),
                "description": "Stress test product"
            },
            headers=self.headers
        )
