#!/usr/bin/env python3
"""
EdRina Resto Order Workflow Test
Tests the complete restaurant order workflow
"""

import requests
import json

BASE_URL = "https://9aabc5f7-575f-4b4b-bbd7-48c6da06e7ea.preview.emergentagent.com/api"

def test_complete_order_workflow():
    """Test complete order workflow from server to payment"""
    print("🍽️ Testing Complete Order Workflow")
    print("=" * 50)
    
    # Step 1: Login as admin and create users
    print("\n1. Setting up users...")
    admin_response = requests.post(f"{BASE_URL}/auth/login", 
                                 json={"username": "admin", "password": "admin123"})
    admin_token = admin_response.json()["access_token"]
    
    # Create test users
    users_to_create = [
        {"username": "serveur_test", "password": "serv123", "role": "serveur"},
        {"username": "chef_test", "password": "chef123", "role": "chef"},
        {"username": "caisse_test", "password": "caisse123", "role": "caisse"}
    ]
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    for user in users_to_create:
        requests.post(f"{BASE_URL}/auth/register", json=user, headers=headers)
    
    print("✅ Test users created")
    
    # Step 2: Login as different roles
    print("\n2. Logging in as different roles...")
    tokens = {}
    for user in users_to_create:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json={"username": user["username"], "password": user["password"]})
        tokens[user["role"]] = response.json()["access_token"]
    
    print("✅ All role tokens obtained")
    
    # Step 3: Get menu items
    print("\n3. Getting menu items...")
    menu_response = requests.get(f"{BASE_URL}/menu")
    menu_items = menu_response.json()
    print(f"✅ Retrieved {len(menu_items)} menu items")
    
    # Step 4: Server creates order
    print("\n4. Server creating order for table 5...")
    order_data = {
        "table_number": 5,
        "items": [
            {
                "menu_item_id": menu_items[0]["id"],
                "menu_item_name": menu_items[0]["name"],
                "quantity": 2,
                "price": menu_items[0]["price"]
            },
            {
                "menu_item_id": menu_items[1]["id"],
                "menu_item_name": menu_items[1]["name"],
                "quantity": 1,
                "price": menu_items[1]["price"]
            }
        ]
    }
    
    server_headers = {"Authorization": f"Bearer {tokens['serveur']}", "Content-Type": "application/json"}
    order_response = requests.post(f"{BASE_URL}/orders", json=order_data, headers=server_headers)
    order = order_response.json()
    order_id = order["id"]
    
    print(f"✅ Order created: ID {order_id}, Table {order['table_number']}, Status: {order['status']}")
    print(f"   Items: {len(order['items'])}, Total: {order['total_amount']} TND")
    
    # Step 5: Chef views kitchen orders
    print("\n5. Chef viewing kitchen orders...")
    chef_headers = {"Authorization": f"Bearer {tokens['chef']}", "Content-Type": "application/json"}
    chef_orders_response = requests.get(f"{BASE_URL}/orders", headers=chef_headers)
    chef_orders = chef_orders_response.json()
    kitchen_orders = [o for o in chef_orders if o["status"] == "in_kitchen"]
    
    print(f"✅ Chef can see {len(kitchen_orders)} orders in kitchen")
    
    # Step 6: Chef marks order as ready
    print("\n6. Chef marking order as ready...")
    update_response = requests.put(f"{BASE_URL}/orders/{order_id}", 
                                 json={"status": "ready"}, 
                                 headers=chef_headers)
    updated_order = update_response.json()
    
    print(f"✅ Order status updated to: {updated_order['status']}")
    if updated_order.get("kitchen_ready_at"):
        print(f"   Kitchen ready timestamp: {updated_order['kitchen_ready_at']}")
    
    # Step 7: Cashier views ready orders
    print("\n7. Cashier viewing ready orders...")
    cashier_headers = {"Authorization": f"Bearer {tokens['caisse']}", "Content-Type": "application/json"}
    cashier_orders_response = requests.get(f"{BASE_URL}/orders", headers=cashier_headers)
    cashier_orders = cashier_orders_response.json()
    ready_orders = [o for o in cashier_orders if o["status"] == "ready"]
    
    print(f"✅ Cashier can see {len(ready_orders)} ready orders")
    
    # Step 8: Cashier processes payment
    print("\n8. Cashier processing payment...")
    payment_response = requests.put(f"{BASE_URL}/orders/{order_id}", 
                                  json={"status": "paid"}, 
                                  headers=cashier_headers)
    final_order = payment_response.json()
    
    print(f"✅ Payment processed! Final status: {final_order['status']}")
    if final_order.get("paid_at"):
        print(f"   Payment timestamp: {final_order['paid_at']}")
    
    # Step 9: Admin views all orders
    print("\n9. Admin viewing all orders...")
    admin_headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    all_orders_response = requests.get(f"{BASE_URL}/orders", headers=admin_headers)
    all_orders = all_orders_response.json()
    
    print(f"✅ Admin can see {len(all_orders)} total orders")
    
    # Verify order status progression
    print("\n" + "=" * 50)
    print("📋 ORDER WORKFLOW VERIFICATION")
    print("=" * 50)
    
    workflow_steps = [
        ("Order Creation", order.get("status") == "in_kitchen"),
        ("Chef Processing", updated_order.get("status") == "ready"),
        ("Payment Processing", final_order.get("status") == "paid"),
        ("Timestamps Set", bool(final_order.get("kitchen_ready_at") and final_order.get("paid_at"))),
        ("Role Access Control", len(kitchen_orders) > 0 and len(ready_orders) > 0)
    ]
    
    passed = 0
    for step_name, success in workflow_steps:
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Workflow Success: {passed}/{len(workflow_steps)} ({passed/len(workflow_steps)*100:.1f}%)")
    
    if passed == len(workflow_steps):
        print("🟢 COMPLETE ORDER WORKFLOW: WORKING PERFECTLY")
        return True
    else:
        print("🔴 COMPLETE ORDER WORKFLOW: ISSUES DETECTED")
        return False

if __name__ == "__main__":
    success = test_complete_order_workflow()
    exit(0 if success else 1)