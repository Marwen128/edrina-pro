#!/usr/bin/env python3
"""
Debug test for restriction check
"""

import requests
import json

BASE_URL = "https://9aabc5f7-575f-4b4b-bbd7-48c6da06e7ea.preview.emergentagent.com/api"

def make_request_debug(method, endpoint, data=None, token=None, timeout=30):
    """Make HTTP request with detailed debugging"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"Making {method} request to: {url}")
    print(f"Headers: {headers}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        if method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        return response
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

# Login and test
print("Logging in as server...")
server_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "serveur_marie",
    "password": "marie123"
}, timeout=30)

if server_response.status_code == 200:
    server_token = server_response.json()["access_token"]
    print("✅ Server login successful")
    
    # Get a ready order ID from recent tests
    orders_response = requests.get(f"{BASE_URL}/orders", headers={
        "Authorization": f"Bearer {server_token}"
    }, timeout=30)
    
    if orders_response.status_code == 200:
        orders = orders_response.json()
        ready_orders = [o for o in orders if o.get("status") == "ready"]
        
        if ready_orders:
            order_id = ready_orders[0]["id"]
            print(f"Testing modification restriction on ready order: {order_id}")
            
            # Try to modify ready order
            modification_data = {
                "items": [
                    {
                        "menu_item_id": "test-id",
                        "menu_item_name": "Test Item",
                        "quantity": 1,
                        "price": 10.0
                    }
                ]
            }
            
            response = make_request_debug("PUT", f"/orders/{order_id}", modification_data, server_token)
            
            if response:
                if response.status_code == 403:
                    print("✅ Restriction working correctly - 403 Forbidden")
                else:
                    print(f"❌ Expected 403, got {response.status_code}")
            else:
                print("❌ No response received")
        else:
            print("No ready orders found for testing")
    else:
        print("Failed to get orders")
else:
    print("Failed to login as server")