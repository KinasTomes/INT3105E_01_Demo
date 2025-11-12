# Locust Configuration for Different Test Scenarios

# Basic Load Test Configuration
# Tests normal user load with realistic wait times

# Load Test - 50 users, spawn rate 5 users/sec
locust -f locustfile.py --host=http://localhost:8080 --users 50 --spawn-rate 5 --run-time 5m --html load_test_report.html

# Stress Test - 200 users, spawn rate 20 users/sec
locust -f locustfile.py --host=http://localhost:8080 --users 200 --spawn-rate 20 --run-time 5m --html stress_test_report.html --user-class StressTest

# Spike Test - Sudden spike to 500 users
locust -f locustfile.py --host=http://localhost:8080 --users 500 --spawn-rate 50 --run-time 3m --html spike_test_report.html

# Endurance Test - 30 users for extended period
locust -f locustfile.py --host=http://localhost:8080 --users 30 --spawn-rate 3 --run-time 30m --html endurance_test_report.html

# Quick Smoke Test - 10 users, 1 minute
locust -f locustfile.py --host=http://localhost:8080 --users 10 --spawn-rate 2 --run-time 1m --html smoke_test_report.html --user-class QuickLoadTest

# Headless mode without Web UI
locust -f locustfile.py --host=http://localhost:8080 --users 100 --spawn-rate 10 --run-time 5m --headless --csv test_results

# With Web UI (manual control)
locust -f locustfile.py --host=http://localhost:8080 --web-port 8089
