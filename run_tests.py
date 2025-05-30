#!/usr/bin/env python3
"""
Comprehensive test runner for Food Delivery Microservices
Runs integration tests, unit tests, and generates coverage reports
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path
import argparse
import json
import pytest
import requests
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy/tests.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Service configurations
SERVICES = {
    'user': {'port': 8001, 'health_endpoint': '/health'},
    'restaurant': {'port': 8002, 'health_endpoint': '/health'},
    'delivery': {'port': 8003, 'health_endpoint': '/health'}
}

def run_command(command, check=True):
    """Run a command and return the result"""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        sys.exit(1)
    
    return result

def setup_test_environment():
    """Set up test environment"""
    print("Setting up test environment...")
    
    print("Creating test database...")
    try:
        run_command([
            "psql", 
            "-h", "localhost", 
            "-U", "postgres", 
            "-c", "CREATE DATABASE mydb_test;"
        ], check=False)
    except:
        print("Test database might already exist or postgres not available")
    
    # Install test dependencies
    print("Installing test dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "httpx", "coverage"])

def run_basic_setup_test():
    """Run basic setup verification"""
    print("\n" + "="*60)
    print("RUNNING BASIC SETUP TESTS")
    print("="*60)
    
    result = run_command([sys.executable, "test_basic_setup.py"], check=False)
    return result.returncode == 0

def run_unit_tests():
    """Run unit tests"""
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    if not Path("tests/unit").exists():
        print("No unit tests directory found, skipping unit tests")
        return True
    
    result = run_command([
        sys.executable, "-m", "pytest", 
        "tests/unit", 
        "-v", 
        "--tb=short"
    ], check=False)
    
    return result.returncode == 0

def run_integration_tests():
    """Run integration tests"""
    print("\n" + "="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60)
    
    if not Path("tests/integration").exists():
        print("No integration tests directory found, skipping integration tests")
        return True
    
    result = run_command([
        sys.executable, "-m", "pytest", 
        "tests/integration", 
        "-v", 
        "--tb=short",
        "-s"  # Don't capture output for better debugging
    ], check=False)
    
    return result.returncode == 0

def run_coverage_tests():
    """Run tests with coverage"""
    print("\n" + "="*60)
    print("RUNNING COVERAGE ANALYSIS")
    print("="*60)
    
    # Run tests with coverage
    run_command([
        sys.executable, "-m", "coverage", "run", 
        "-m", "pytest", 
        "tests/", 
        "-v"
    ], check=False)
    
    # Generate coverage report
    run_command([sys.executable, "-m", "coverage", "report"], check=False)
    
    # Generate HTML coverage report
    run_command([sys.executable, "-m", "coverage", "html"], check=False)
    print("\nHTML coverage report generated in htmlcov/index.html")

def check_service(name: str, port: int, health_endpoint: str) -> bool:
    """Check if a service is accessible and healthy."""
    url = f'http://localhost:{port}{health_endpoint}'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logger.info(f"[PASS] {name} is accessible at {url}")
            return True
        else:
            logger.error(f"[FAIL] {name} returned status {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"[FAIL] {name} is not accessible at {url}: {e}")
        return False

def load_test_postman_collection() -> bool:
    """Load and validate the Postman collection."""
    collection_path = Path('postman/Food_Delivery_API_Collection.json')
    try:
        with open(collection_path) as f:
            collection = json.load(f)
        logger.info(f"[PASS] Postman collection loaded successfully")
        logger.info(f"Found {len(collection['item'])} requests across {len(collection['item'])} folders")
        return True
    except Exception as e:
        logger.error(f"[FAIL] Error loading Postman collection: {e}")
        return False

def validate_docker_setup() -> bool:
    """Validate Docker configuration files."""
    required_files = [
        'deploy/docker-compose.yml',
        'user_service/Dockerfile',
        'restaurant_service/Dockerfile',
        'delivery_service/Dockerfile',
        'deploy/nginx/nginx.conf'
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            logger.info(f"[PASS] {file}")
        else:
            logger.error(f"[FAIL] {file} not found")
            all_present = False
    
    if all_present:
        logger.info("[PASS] All Docker configuration files present")
    return all_present

def run_pytest_tests() -> tuple[int, int]:
    """Run pytest tests and return (passed, total) counts."""
    try:
        result = pytest.main(['-v', 'tests/'])
        passed = 0
        total = 0
        with open('deploy/tests.log', 'r') as f:
            for line in f:
                if 'PASSED' in line:
                    passed += 1
                    total += 1
                elif 'FAILED' in line:
                    total += 1
        return passed, total
    except Exception as e:
        logger.error(f"[FAIL] Error running tests: {e}")
        return 0, 0

def test_services_running():
    """Test if services are running and accessible"""
    print("\n" + "="*60)
    print("TESTING SERVICE ACCESSIBILITY")
    print("="*60)
    
    import httpx
    import asyncio
    
    async def check_service(url, name):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    print(f"[PASS] {name} is accessible at {url}")
                    return True
                else:
                    print(f"[FAIL] {name} returned status {response.status_code}")
                    return False
        except Exception as e:
            print(f"[FAIL] {name} is not accessible at {url}: {e}")
            return False
    
    async def check_all_services():
        services = [
            ("http://localhost:8001", "User Service"),
            ("http://localhost:8002", "Restaurant Service"), 
            ("http://localhost:8003", "Delivery Service")
        ]
        
        results = await asyncio.gather(*[
            check_service(url, name) for url, name in services
        ])
        
        return all(results)
    
    return asyncio.run(check_all_services())

def load_test_postman_collection():
    """Test Postman collection structure"""
    print("\n" + "="*60)
    print("VALIDATING POSTMAN COLLECTION")
    print("="*60)
    
    import json
    
    try:
        with open("postman/Food_Delivery_API_Collection.json", "r") as f:
            collection = json.load(f)
        
        print(f"[PASS] Postman collection loaded successfully")
        print(f"   Collection name: {collection['info']['name']}")
        print(f"   Number of folders: {len(collection['item'])}")
        
        total_requests = 0
        for folder in collection['item']:
            requests_in_folder = len(folder['item'])
            total_requests += requests_in_folder
            print(f"   - {folder['name']}: {requests_in_folder} requests")
        
        print(f"   Total requests: {total_requests}")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error loading Postman collection: {e}")
        return False

def validate_docker_setup():
    """Validate Docker setup"""
    print("\n" + "="*60)
    print("VALIDATING DOCKER SETUP")
    print("="*60)
    
    docker_files = [
        "Dockerfile.user_service",
        "Dockerfile.restaurant_service", 
        "Dockerfile.delivery_service",
        "docker-compose.yml",
        "nginx.conf"
    ]
    
    all_exist = True
    for file in docker_files:
        if Path(file).exists():
            print(f"[PASS] {file}")
        else:
            print(f"[FAIL] {file} not found")
            all_exist = False
    
    if all_exist:
        print("[PASS] All Docker configuration files present")
    
    return all_exist

def main():
    parser = argparse.ArgumentParser(description="Food Delivery Microservices Test Runner")
    parser.add_argument("--basic", action="store_true", help="Run only basic setup tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--services", action="store_true", help="Test service accessibility")
    parser.add_argument("--postman", action="store_true", help="Validate Postman collection")
    parser.add_argument("--docker", action="store_true", help="Validate Docker setup")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--no-setup", action="store_true", help="Skip test environment setup")
    
    args = parser.parse_args()
    
    # If no specific test type is chosen, run all
    if not any([args.basic, args.unit, args.integration, args.coverage, 
                args.services, args.postman, args.docker]):
        args.all = True
    
    print("🧪 Food Delivery Microservices Test Suite")
    print("=" * 50)
    
    results = {}
    
    # Setup test environment
    if not args.no_setup:
        setup_test_environment()
    
    # Run selected tests
    if args.basic or args.all:
        results['basic'] = run_basic_setup_test()
    
    if args.unit or args.all:
        results['unit'] = run_unit_tests()
    
    if args.integration or args.all:
        results['integration'] = run_integration_tests()
    
    if args.coverage or args.all:
        run_coverage_tests()  # Always passes, just generates report
    
    if args.services or args.all:
        results['services'] = test_services_running()
    
    if args.postman or args.all:
        results['postman'] = load_test_postman_collection()
    
    if args.docker or args.all:
        results['docker'] = validate_docker_setup()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = 0
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name.upper():20s}: {status}")
        if result:
            passed += 1
        total += 1
    
    print("-" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Your microservices are ready for deployment.")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 