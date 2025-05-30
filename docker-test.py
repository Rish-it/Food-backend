#!/usr/bin/env python3
"""
Simple Docker test script to verify all services are running
"""

import asyncio
import httpx
import sys

SERVICES = {
    "GraphQL Gateway": "http://localhost:8000/health",
    "User Service": "http://localhost:8001/health",
    "Restaurant Service": "http://localhost:8002/health",
    "Delivery Service": "http://localhost:8003/health"
}

async def test_service_health():
    """Test if all services are healthy"""
    print("Testing service health...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        all_healthy = True
        
        for service_name, health_url in SERVICES.items():
            try:
                response = await client.get(health_url)
                if response.status_code == 200:
                    print(f"✓ {service_name}: HEALTHY")
                else:
                    print(f"✗ {service_name}: UNHEALTHY (Status: {response.status_code})")
                    all_healthy = False
            except Exception as e:
                print(f"✗ {service_name}: CONNECTION FAILED ({e})")
                all_healthy = False
        
        return all_healthy

async def main():
    """Main test function"""
    print("Docker Environment Health Check")
    print("=" * 40)
    
    if await test_service_health():
        print("\n✓ All services are healthy!")
        print("\nService URLs:")
        print("- GraphQL Gateway: http://localhost:8000/graphql")
        print("- User Service API: http://localhost:8001/docs")
        print("- Restaurant Service API: http://localhost:8002/docs")
        print("- Delivery Service API: http://localhost:8003/docs")
        return 0
    else:
        print("\n✗ Some services are not healthy!")
        print("Try: make logs to check service logs")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 