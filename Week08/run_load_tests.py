#!/usr/bin/env python3
"""
Locust Test Runner Script
Automates running different load testing scenarios
"""

import subprocess
import sys
import os
from datetime import datetime


class Colors:
    """Terminal colors for pretty output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def run_test(name, users, spawn_rate, duration, locustfile="locustfile.py", host="http://localhost:8080"):
    """Run a locust test with given parameters"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"{name.lower().replace(' ', '_')}_{timestamp}"
    
    print_header(f"Running {name}")
    print_info(f"Users: {users} | Spawn Rate: {spawn_rate}/sec | Duration: {duration}")
    print_info(f"Using: {locustfile}")
    print_info(f"Report: {report_name}.html")
    
    cmd = [
        "locust",
        "-f", locustfile,
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", duration,
        "--headless",
        "--html", f"{report_name}.html",
        "--csv", report_name
    ]
    
    try:
        print_info("Starting test...")
        result = subprocess.run(cmd, check=True)
        print_success(f"{name} completed successfully!")
        print_success(f"Report saved: {report_name}.html")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{name} failed with error code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print_error("Test interrupted by user")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("Checking Dependencies")
    
    # Check if locust is installed
    try:
        result = subprocess.run(["locust", "--version"], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        version = result.stdout.strip()
        print_success(f"Locust is installed: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Locust is not installed!")
        print_info("Install with: pip install locust")
        return False


def check_server(host="http://localhost:8080"):
    """Check if API server is running"""
    print_header("Checking API Server")
    
    try:
        import requests
        response = requests.get(f"{host}/docs", timeout=5)
        if response.status_code == 200:
            print_success(f"API Server is running at {host}")
            return True
        else:
            print_error(f"API Server returned status code: {response.status_code}")
            return False
    except ImportError:
        print_info("requests module not found, skipping server check")
        print_info("Install with: pip install requests")
        return True  # Don't block test if requests is not available
    except Exception as e:
        print_error(f"Cannot connect to API server at {host}")
        print_error(f"Error: {str(e)}")
        print_info("Make sure server is running with: uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080")
        return False


def main():
    """Main function"""
    print_header("Locust Load Testing Automation")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Get host from environment or use default
    host = os.getenv("API_HOST", "http://localhost:8080")
    
    # Check if server is running
    if not check_server(host):
        response = input("\nAPI server is not responding. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print_info("Exiting...")
            sys.exit(1)
    
    # Display menu
    print_header("Available Test Scenarios")
    print(f"{Colors.BOLD}1.{Colors.ENDC} Smoke Test (Quick validation - 10 users, 1 min)")
    print(f"{Colors.BOLD}2.{Colors.ENDC} Load Test (Normal load - 50 users, 5 min)")
    print(f"{Colors.BOLD}3.{Colors.ENDC} Stress Test (High load - 200 users, 5 min)")
    print(f"{Colors.BOLD}4.{Colors.ENDC} Spike Test (Sudden spike - 500 users, 3 min)")
    print(f"{Colors.BOLD}5.{Colors.ENDC} Endurance Test (Long duration - 30 users, 30 min)")
    print(f"{Colors.BOLD}6.{Colors.ENDC} Quick Load Test (Read-heavy - 100 users, 5 min)")
    print(f"{Colors.BOLD}7.{Colors.ENDC} Run All Tests (Sequential)")
    print(f"{Colors.BOLD}8.{Colors.ENDC} Custom Test")
    print(f"{Colors.BOLD}9.{Colors.ENDC} Interactive Mode (Web UI)")
    print(f"{Colors.BOLD}0.{Colors.ENDC} Exit")
    
    try:
        choice = input(f"\n{Colors.BOLD}Select test scenario (0-9): {Colors.ENDC}")
        
        if choice == "1":
            run_test("Smoke Test", 10, 2, "1m", "locustfile_quick.py", host)
        
        elif choice == "2":
            run_test("Load Test", 50, 5, "5m", "locustfile.py", host)
        
        elif choice == "3":
            run_test("Stress Test", 200, 20, "5m", "locustfile_stress.py", host)
        
        elif choice == "4":
            run_test("Spike Test", 500, 50, "3m", "locustfile.py", host)
        
        elif choice == "5":
            run_test("Endurance Test", 30, 3, "30m", "locustfile.py", host)
        
        elif choice == "6":
            run_test("Quick Load Test", 100, 10, "5m", "locustfile_quick.py", host)
        
        elif choice == "7":
            print_header("Running All Tests")
            tests = [
                ("Smoke Test", 10, 2, "1m", "locustfile_quick.py"),
                ("Load Test", 50, 5, "5m", "locustfile.py"),
                ("Stress Test", 200, 20, "5m", "locustfile_stress.py"),
            ]
            
            success_count = 0
            for name, users, spawn_rate, duration, locustfile in tests:
                if run_test(name, users, spawn_rate, duration, locustfile, host):
                    success_count += 1
                print("\n")
            
            print_header("Test Summary")
            print_info(f"Completed {success_count}/{len(tests)} tests successfully")
        
        elif choice == "8":
            print_header("Custom Test Configuration")
            users = int(input("Number of users: "))
            spawn_rate = int(input("Spawn rate (users/sec): "))
            duration = input("Duration (e.g., 5m, 30s): ")
            print("\nAvailable locustfiles:")
            print("  1. locustfile.py (Default - Sequential behavior)")
            print("  2. locustfile_quick.py (Quick/Smoke test - Read-heavy)")
            print("  3. locustfile_stress.py (Stress test - Aggressive)")
            locustfile_choice = input("Choose locustfile (1-3, default=1): ").strip()
            
            locustfile_map = {
                "1": "locustfile.py",
                "2": "locustfile_quick.py",
                "3": "locustfile_stress.py",
                "": "locustfile.py"
            }
            locustfile = locustfile_map.get(locustfile_choice, "locustfile.py")
            
            run_test("Custom Test", users, spawn_rate, duration, locustfile, host)
        
        elif choice == "9":
            print_header("Interactive Mode - Web UI")
            print_info("Starting Locust with Web UI...")
            print_info(f"Access at: http://localhost:8089")
            print_info("Press Ctrl+C to stop")
            
            cmd = ["locust", "-f", "locustfile.py", "--host", host]
            subprocess.run(cmd)
        
        elif choice == "0":
            print_info("Exiting...")
            sys.exit(0)
        
        else:
            print_error("Invalid choice!")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print_error("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
