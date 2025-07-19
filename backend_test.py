#!/usr/bin/env python3
"""
EdRina Resto Backend API Testing Suite
Tests the complete restaurant management system backend
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://9aabc5f7-575f-4b4b-bbd7-48c6da06e7ea.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class EdRinaRestoTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.server_token = None
        self.chef_token = None
        self.cashier_token = None
        self.test_results = []
        self.created_users = []
        self.created_menu_items = []
        self.created_orders = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def make_request(self, method, endpoint, data=None, token=None, expected_status=200):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def test_system_initialization(self):
        """Test system initialization endpoint"""
        print("\n=== Testing System Initialization ===")
        
        response = self.make_request("POST", "/init")
        if response and response.status_code in [200, 201]:
            data = response.json()
            if "admin" in data.get("message", "").lower():
                self.log_test("System Initialization", True, "Admin user and sample menu created successfully")
                return True
            else:
                self.log_test("System Initialization", False, f"Unexpected response: {data}")
                return False
        else:
            error_msg = response.text if response else "No response"
            self.log_test("System Initialization", False, f"Failed with status {response.status_code if response else 'None'}: {error_msg}")
            return False
    
    def test_admin_login(self):
        """Test admin login"""
        print("\n=== Testing Admin Authentication ===")
        
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data and data.get("user", {}).get("role") == "admin":
                self.admin_token = data["access_token"]
                self.log_test("Admin Login", True, f"Successfully logged in as admin: {data['user']['username']}")
                return True
            else:
                self.log_test("Admin Login", False, f"Invalid response structure: {data}")
                return False
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Admin Login", False, f"Login failed with status {response.status_code if response else 'None'}: {error_msg}")
            return False
    
    def test_user_management(self):
        """Test user management (admin creating users)"""
        print("\n=== Testing User Management ===")
        
        if not self.admin_token:
            self.log_test("User Management", False, "No admin token available")
            return False
        
        # Test creating users with different roles
        test_users = [
            {"username": "serveur_marie", "password": "marie123", "role": "serveur"},
            {"username": "chef_ahmed", "password": "ahmed123", "role": "chef"},
            {"username": "caisse_fatma", "password": "fatma123", "role": "caisse"}
        ]
        
        success_count = 0
        for user_data in test_users:
            response = self.make_request("POST", "/auth/register", user_data, self.admin_token)
            if response and response.status_code in [200, 201]:
                data = response.json()
                if "user" in data and data["user"]["role"] == user_data["role"]:
                    self.created_users.append(data["user"])
                    success_count += 1
                    self.log_test(f"Create {user_data['role']} user", True, f"Created user: {user_data['username']}")
                else:
                    self.log_test(f"Create {user_data['role']} user", False, f"Invalid response: {data}")
            else:
                error_msg = response.text if response else "No response"
                self.log_test(f"Create {user_data['role']} user", False, f"Failed: {error_msg}")
        
        # Test getting all users
        response = self.make_request("GET", "/users", token=self.admin_token)
        if response and response.status_code == 200:
            users = response.json()
            if len(users) >= 4:  # admin + 3 created users
                self.log_test("Get All Users", True, f"Retrieved {len(users)} users")
            else:
                self.log_test("Get All Users", False, f"Expected at least 4 users, got {len(users)}")
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Get All Users", False, f"Failed: {error_msg}")
        
        return success_count == len(test_users)
    
    def test_role_based_login(self):
        """Test login for different roles"""
        print("\n=== Testing Role-Based Authentication ===")
        
        role_logins = [
            {"username": "serveur_marie", "password": "marie123", "role": "serveur"},
            {"username": "chef_ahmed", "password": "ahmed123", "role": "chef"},
            {"username": "caisse_fatma", "password": "fatma123", "role": "caisse"}
        ]
        
        tokens = {}
        success_count = 0
        
        for login_data in role_logins:
            response = self.make_request("POST", "/auth/login", {
                "username": login_data["username"],
                "password": login_data["password"]
            })
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get("user", {}).get("role") == login_data["role"]:
                    tokens[login_data["role"]] = data["access_token"]
                    success_count += 1
                    self.log_test(f"{login_data['role']} login", True, f"Successfully logged in as {login_data['username']}")
                else:
                    self.log_test(f"{login_data['role']} login", False, f"Role mismatch: {data}")
            else:
                error_msg = response.text if response else "No response"
                self.log_test(f"{login_data['role']} login", False, f"Failed: {error_msg}")
        
        # Store tokens for later use
        self.server_token = tokens.get("serveur")
        self.chef_token = tokens.get("chef")
        self.cashier_token = tokens.get("caisse")
        
        return success_count == len(role_logins)
    
    def test_menu_management(self):
        """Test menu management operations"""
        print("\n=== Testing Menu Management ===")
        
        if not self.admin_token:
            self.log_test("Menu Management", False, "No admin token available")
            return False
        
        # Test getting existing menu (should have sample items from init)
        response = self.make_request("GET", "/menu")
        if response and response.status_code == 200:
            menu_items = response.json()
            if len(menu_items) >= 5:  # Sample menu has 5 items
                self.log_test("Get Menu Items", True, f"Retrieved {len(menu_items)} menu items")
            else:
                self.log_test("Get Menu Items", False, f"Expected at least 5 items, got {len(menu_items)}")
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Get Menu Items", False, f"Failed: {error_msg}")
            return False
        
        # Test creating new menu item (admin)
        new_item = {
            "name": "Lablabi Tunisien",
            "description": "Soupe de pois chiches traditionnelle",
            "price": 7.5
        }
        
        response = self.make_request("POST", "/menu", new_item, self.admin_token)
        if response and response.status_code in [200, 201]:
            data = response.json()
            if data.get("name") == new_item["name"]:
                self.created_menu_items.append(data)
                self.log_test("Create Menu Item (Admin)", True, f"Created: {new_item['name']}")
            else:
                self.log_test("Create Menu Item (Admin)", False, f"Invalid response: {data}")
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Create Menu Item (Admin)", False, f"Failed: {error_msg}")
        
        # Test creating menu item as chef
        if self.chef_token:
            chef_item = {
                "name": "Harissa Maison",
                "description": "Sauce harissa faite maison",
                "price": 3.0
            }
            
            response = self.make_request("POST", "/menu", chef_item, self.chef_token)
            if response and response.status_code in [200, 201]:
                data = response.json()
                if data.get("name") == chef_item["name"]:
                    self.created_menu_items.append(data)
                    self.log_test("Create Menu Item (Chef)", True, f"Created: {chef_item['name']}")
                else:
                    self.log_test("Create Menu Item (Chef)", False, f"Invalid response: {data}")
            else:
                error_msg = response.text if response else "No response"
                self.log_test("Create Menu Item (Chef)", False, f"Failed: {error_msg}")
        
        return True
    
    def test_order_workflow(self):
        """Test complete order workflow"""
        print("\n=== Testing Order Workflow ===")
        
        if not all([self.server_token, self.chef_token, self.cashier_token]):
            self.log_test("Order Workflow", False, "Missing required role tokens")
            return False
        
        # Get menu items for order
        response = self.make_request("GET", "/menu")
        if not response or response.status_code != 200:
            self.log_test("Order Workflow", False, "Cannot retrieve menu items")
            return False
        
        menu_items = response.json()
        if len(menu_items) < 2:
            self.log_test("Order Workflow", False, "Not enough menu items for testing")
            return False
        
        # Step 1: Server creates order
        order_data = {
            "table_number": 3,
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
        
        response = self.make_request("POST", "/orders", order_data, self.server_token)
        if response and response.status_code in [200, 201]:
            order = response.json()
            if order.get("status") == "in_kitchen" and order.get("table_number") == 3:
                self.created_orders.append(order)
                self.log_test("Server Create Order", True, f"Order created for table {order['table_number']}")
                order_id = order["id"]
            else:
                self.log_test("Server Create Order", False, f"Invalid order response: {order}")
                return False
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Server Create Order", False, f"Failed: {error_msg}")
            return False
        
        # Step 2: Chef views orders and marks ready
        response = self.make_request("GET", "/orders", token=self.chef_token)
        if response and response.status_code == 200:
            chef_orders = response.json()
            kitchen_orders = [o for o in chef_orders if o["status"] == "in_kitchen"]
            if len(kitchen_orders) > 0:
                self.log_test("Chef View Kitchen Orders", True, f"Chef can see {len(kitchen_orders)} kitchen orders")
            else:
                self.log_test("Chef View Kitchen Orders", False, "No kitchen orders visible to chef")
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Chef View Kitchen Orders", False, f"Failed: {error_msg}")
        
        # Chef marks order as ready
        update_data = {"status": "ready"}
        response = self.make_request("PUT", f"/orders/{order_id}", update_data, self.chef_token)
        if response and response.status_code == 200:
            updated_order = response.json()
            if updated_order.get("status") == "ready":
                self.log_test("Chef Mark Order Ready", True, "Order marked as ready by chef")
            else:
                self.log_test("Chef Mark Order Ready", False, f"Status not updated: {updated_order}")
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Chef Mark Order Ready", False, f"Failed: {error_msg}")
        
        # Step 3: Cashier views ready orders and processes payment
        response = self.make_request("GET", "/orders", token=self.cashier_token)
        if response and response.status_code == 200:
            cashier_orders = response.json()
            ready_orders = [o for o in cashier_orders if o["status"] == "ready"]
            if len(ready_orders) > 0:
                self.log_test("Cashier View Ready Orders", True, f"Cashier can see {len(ready_orders)} ready orders")
            else:
                self.log_test("Cashier View Ready Orders", False, "No ready orders visible to cashier")
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Cashier View Ready Orders", False, f"Failed: {error_msg}")
        
        # Cashier processes payment
        payment_data = {"status": "paid"}
        response = self.make_request("PUT", f"/orders/{order_id}", payment_data, self.cashier_token)
        if response and response.status_code == 200:
            paid_order = response.json()
            if paid_order.get("status") == "paid":
                self.log_test("Cashier Process Payment", True, "Payment processed successfully")
            else:
                self.log_test("Cashier Process Payment", False, f"Status not updated: {paid_order}")
        else:
            error_msg = response.text if response else "No response"
            self.log_test("Cashier Process Payment", False, f"Failed: {error_msg}")
        
        return True
    
    def test_role_based_access_control(self):
        """Test role-based access control"""
        print("\n=== Testing Role-Based Access Control ===")
        
        # Test server trying to access admin endpoint (should fail)
        if self.server_token:
            response = self.make_request("GET", "/users", token=self.server_token)
            if response and response.status_code == 403:
                self.log_test("Server Access Control", True, "Server correctly denied access to user management")
            else:
                self.log_test("Server Access Control", False, f"Server should be denied access, got status: {response.status_code if response else 'None'}")
        
        # Test chef trying to register user (should fail)
        if self.chef_token:
            user_data = {"username": "test_user", "password": "test123", "role": "serveur"}
            response = self.make_request("POST", "/auth/register", user_data, self.chef_token)
            if response and response.status_code == 403:
                self.log_test("Chef Access Control", True, "Chef correctly denied user registration")
            else:
                self.log_test("Chef Access Control", False, f"Chef should be denied user registration, got status: {response.status_code if response else 'None'}")
        
        # Test cashier trying to create order (should fail)
        if self.cashier_token:
            order_data = {
                "table_number": 5,
                "items": [{"menu_item_id": "test", "menu_item_name": "test", "quantity": 1, "price": 10.0}]
            }
            response = self.make_request("POST", "/orders", order_data, self.cashier_token)
            if response and response.status_code == 403:
                self.log_test("Cashier Access Control", True, "Cashier correctly denied order creation")
            else:
                self.log_test("Cashier Access Control", False, f"Cashier should be denied order creation, got status: {response.status_code if response else 'None'}")
        
        return True
    
    def test_table_validation(self):
        """Test table number validation (1-8)"""
        print("\n=== Testing Table Validation ===")
        
        if not self.server_token:
            self.log_test("Table Validation", False, "No server token available")
            return False
        
        # Test invalid table numbers
        invalid_tables = [0, 9, -1, 15]
        for table_num in invalid_tables:
            order_data = {
                "table_number": table_num,
                "items": [{"menu_item_id": "test", "menu_item_name": "test", "quantity": 1, "price": 10.0}]
            }
            response = self.make_request("POST", "/orders", order_data, self.server_token)
            if response and response.status_code == 400:
                self.log_test(f"Invalid Table {table_num}", True, f"Table {table_num} correctly rejected")
            else:
                self.log_test(f"Invalid Table {table_num}", False, f"Table {table_num} should be rejected, got status: {response.status_code if response else 'None'}")
        
        return True
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting EdRina Resto Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("System Initialization", self.test_system_initialization),
            ("Admin Authentication", self.test_admin_login),
            ("User Management", self.test_user_management),
            ("Role-Based Login", self.test_role_based_login),
            ("Menu Management", self.test_menu_management),
            ("Order Workflow", self.test_order_workflow),
            ("Role-Based Access Control", self.test_role_based_access_control),
            ("Table Validation", self.test_table_validation)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test failed with exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        success_tests = [t for t in self.test_results if t["success"]]
        failed_tests = [t for t in self.test_results if not t["success"]]
        
        print(f"✅ Passed: {len(success_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"📊 Success Rate: {len(success_tests)}/{len(self.test_results)} ({len(success_tests)/len(self.test_results)*100:.1f}%)")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")
        
        print("\n🎯 CRITICAL FUNCTIONALITY STATUS:")
        critical_functions = [
            "System Initialization",
            "Admin Login", 
            "Server Create Order",
            "Chef Mark Order Ready",
            "Cashier Process Payment"
        ]
        
        for func in critical_functions:
            test_result = next((t for t in self.test_results if func.lower() in t['test'].lower()), None)
            if test_result:
                status = "✅" if test_result['success'] else "❌"
                print(f"   {status} {func}")
        
        return len(success_tests), len(failed_tests)

if __name__ == "__main__":
    tester = EdRinaRestoTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)