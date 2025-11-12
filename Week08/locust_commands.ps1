# Locust Load Testing Scripts - PowerShell
# Run these commands from PowerShell in Windows

# 1. Basic Load Test - 50 concurrent users
# Simulates normal traffic with 50 users, spawning 5 users per second
locust -f locustfile.py --host=http://localhost:8080 --users 50 --spawn-rate 5 --run-time 5m --html load_test_report.html

# 2. Stress Test - 200 concurrent users (aggressive)
# Tests system under heavy load
locust -f locustfile_stress.py --host=http://localhost:8080 --users 200 --spawn-rate 20 --run-time 5m --html stress_test_report.html

# 3. Spike Test - Sudden spike to 500 users
# Tests how system handles sudden traffic increase
locust -f locustfile.py --host=http://localhost:8080 --users 500 --spawn-rate 50 --run-time 3m --html spike_test_report.html

# 4. Endurance Test - Long duration test (30 minutes)
# Tests system stability over extended period
locust -f locustfile.py --host=http://localhost:8080 --users 30 --spawn-rate 3 --run-time 30m --html endurance_test_report.html

# 5. Quick Smoke Test - Fast validation
# Quick test with read-heavy operations
locust -f locustfile_quick.py --host=http://localhost:8080 --users 10 --spawn-rate 2 --run-time 1m --html smoke_test_report.html

# 6. Headless Mode - No Web UI, export to CSV
# Run test in headless mode with CSV output
locust -f locustfile.py --host=http://localhost:8080 --users 100 --spawn-rate 10 --run-time 5m --headless --csv test_results

# 7. Sequential User Behavior Test
# Tests realistic user journey
locust -f locustfile.py --host=http://localhost:8080 --users 30 --spawn-rate 5 --run-time 5m --html sequential_test_report.html

# 8. Interactive Mode - Web UI
# Start Locust with Web UI for manual control
# Access at http://localhost:8089
locust -f locustfile.py --host=http://localhost:8080 --web-port 8089

# 9. Distributed Load Testing - Master node
# For running distributed tests (master)
locust -f locustfile.py --host=http://localhost:8080 --master --expect-workers 2

# 10. Distributed Load Testing - Worker node
# For running distributed tests (worker)
locust -f locustfile.py --host=http://localhost:8080 --worker --master-host=localhost

# Additional useful options:
# --csv-full-history : Export full history to CSV
# --loglevel DEBUG : Set log level
# --logfile test.log : Save logs to file
# --stop-timeout 10 : Wait time before stopping
