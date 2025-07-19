#!/usr/bin/env python3
"""
Focused test for Order Modification functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://9aabc5f7-575f-4b4b-bbd7-48c6da06e7ea.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def make_request(method, endpoint, data=None, token=None, timeout=60):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def test_order_modification():
    """Test order modification functionality"""
    print("🧪 Testing Order Modification Functionality")
    print("=" * 50)
    
    # Step 1: Login as admin and get tokens
    print("1. Logging in as admin...")
    admin_response = make_request("POST", "/auth/login", {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    })
    
    if not admin_response or admin_response.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_token = admin_response.json()["access_token"]
    print("✅ Admin login successful")
    
    # Step 2: Login as server
    print("2. Logging in as server...")
    server_response = make_request("POST", "/auth/login", {
        "username": "serveur_marie",
        "password": "marie123"
    })
    
    if not server_response or server_response.status_code != 200:
        print("❌ Server login failed")
        return False
    
    server_token = server_response.json()["access_token"]
    print("✅ Server login successful")
    
    # Step 3: Login as chef
    print("3. Logging in as chef...")
    chef_response = make_request("POST", "/auth/login", {
        "username": "chef_ahmed",
        "password": "ahmed123"
    })
    
    if not chef_response or chef_response.status_code != 200:
        print("❌ Chef login failed")
        return False
    
    chef_token = chef_response.json()["access_token"]
    print("✅ Chef login successful")
    
    # Step 4: Get menu items
    print("4. Getting menu items...")
    menu_response = make_request("GET", "/menu")
    if not menu_response or menu_response.status_code != 200:
        print("❌ Failed to get menu items")
        return False
    
    menu_items = menu_response.json()
    print(f"✅ Retrieved {len(menu_items)} menu items")
    
    # Step 5: Create initial order
    print("5. Creating initial order...")
    order_data = {
        "table_number": 6,
        "items": [
            {
                "menu_item_id": menu_items[0]["id"],
                "menu_item_name": menu_items[0]["name"],
                "quantity": 1,
                "price": menu_items[0]["price"]
            },
            {
                "menu_item_id": menu_items[1]["id"],
                "menu_item_name": menu_items[1]["name"],
                "quantity": 2,
                "price": menu_items[1]["price"]
            }
        ]
    }
    
    order_response = make_request("POST", "/orders", order_data, server_token)
    if not order_response or order_response.status_code not in [200, 201]:
        print("❌ Failed to create order")
        return False
    
    order = order_response.json()
    order_id = order["id"]
    initial_total = order["total_amount"]
    print(f"✅ Order created with ID: {order_id}, Total: {initial_total} TND")
    
    # Step 6: Test order modification - Add items and change quantities
    print("6. Testing order modification...")
    modified_items = [
        # Keep first item but increase quantity
        {
            "menu_item_id": menu_items[0]["id"],
            "menu_item_name": menu_items[0]["name"],
            "quantity": 3,  # Changed from 1 to 3
            "price": menu_items[0]["price"]
        },
        # Keep second item same
        {
            "menu_item_id": menu_items[1]["id"],
            "menu_item_name": menu_items[1]["name"],
            "quantity": 2,
            "price": menu_items[1]["price"]
        },
        # Add new third item
        {
            "menu_item_id": menu_items[2]["id"],
            "menu_item_name": menu_items[2]["name"],
            "quantity": 1,
            "price": menu_items[2]["price"]
        }
    ]
    
    modification_data = {"items": modified_items}
    modify_response = make_request("PUT", f"/orders/{order_id}", modification_data, server_token)
    
    if not modify_response or modify_response.status_code != 200:
        print(f"❌ Order modification failed: {modify_response.text if modify_response else 'No response'}")
        return False
    
    modified_order = modify_response.json()
    new_total = modified_order["total_amount"]
    expected_total = sum(item["price"] * item["quantity"] for item in modified_items)
    
    print(f"✅ Order modified successfully!")
    print(f"   Original total: {initial_total} TND")
    print(f"   New total: {new_total} TND")
    print(f"   Expected total: {expected_total} TND")
    
    if abs(new_total - expected_total) < 0.01:
        print("✅ Total calculation is correct")
    else:
        print("❌ Total calculation is incorrect")
        return False
    
    # Step 7: Test removing items
    print("7. Testing item removal...")
    reduced_items = [
        # Keep only first item with reduced quantity
        {
            "menu_item_id": menu_items[0]["id"],
            "menu_item_name": menu_items[0]["name"],
            "quantity": 1,
            "price": menu_items[0]["price"]
        }
    ]
    
    reduction_data = {"items": reduced_items}
    reduce_response = make_request("PUT", f"/orders/{order_id}", reduction_data, server_token)
    
    if not reduce_response or reduce_response.status_code != 200:
        print(f"❌ Item removal failed: {reduce_response.text if reduce_response else 'No response'}")
        return False
    
    reduced_order = reduce_response.json()
    final_total = reduced_order["total_amount"]
    expected_final = menu_items[0]["price"] * 1
    
    print(f"✅ Items removed successfully!")
    print(f"   Final total: {final_total} TND")
    print(f"   Expected final: {expected_final} TND")
    
    # Step 8: Test chef marking order as ready
    print("8. Testing chef workflow...")
    chef_update = {"status": "ready"}
    chef_response = make_request("PUT", f"/orders/{order_id}", chef_update, chef_token)
    
    if not chef_response or chef_response.status_code != 200:
        print(f"❌ Chef update failed: {chef_response.text if chef_response else 'No response'}")
        return False
    
    ready_order = chef_response.json()
    if ready_order.get("status") == "ready":
        print("✅ Chef marked order as ready")
    else:
        print("❌ Order status not updated correctly")
        return False
    
    # Step 9: Test server cannot modify after ready
    print("9. Testing modification restriction after ready...")
    final_modification = {
        "items": [
            {
                "menu_item_id": menu_items[0]["id"],
                "menu_item_name": menu_items[0]["name"],
                "quantity": 5,
                "price": menu_items[0]["price"]
            }
        ]
    }
    
    restriction_response = make_request("PUT", f"/orders/{order_id}", final_modification, server_token)
    
    if restriction_response and restriction_response.status_code == 403:
        print("✅ Server correctly denied modification of ready order")
    else:
        print(f"❌ Server should be denied modification, got status: {restriction_response.status_code if restriction_response else 'None'}")
        return False
    
    print("\n🎉 All order modification tests passed!")
    return True

if __name__ == "__main__":
    success = test_order_modification()
    if success:
        print("\n✅ ORDER MODIFICATION FUNCTIONALITY IS WORKING CORRECTLY")
    else:
        print("\n❌ ORDER MODIFICATION FUNCTIONALITY HAS ISSUES")
    
    exit(0 if success else 1)