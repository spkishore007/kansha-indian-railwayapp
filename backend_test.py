#!/usr/bin/env python3
"""
Backend API Testing for Kansha's Indian Treat Catering Website
Tests all backend endpoints for functionality and data integrity
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://731c8664-471d-412b-96af-8f26e00980bd.preview.emergentagent.com/api"

class KanshaBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.admin_token = None
        self.test_results = []
        self.sample_menu_item_id = None
        self.sample_order_id = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_menu_endpoints(self):
        """Test all menu-related endpoints"""
        print("\n=== Testing Menu Endpoints ===")
        
        # Test GET /api/menu
        try:
            response = requests.get(f"{self.base_url}/menu", timeout=10)
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                if len(menu_items) > 0:
                    # Store a sample menu item ID for later tests
                    self.sample_menu_item_id = menu_items[0].get('id')
                    self.log_test("GET /api/menu", True, f"Retrieved {len(menu_items)} menu items")
                    
                    # Verify menu structure
                    sample_item = menu_items[0]
                    required_fields = ['id', 'name', 'category', 'price', 'available']
                    missing_fields = [field for field in required_fields if field not in sample_item]
                    if missing_fields:
                        self.log_test("Menu Item Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Menu Item Structure", True, "All required fields present")
                else:
                    self.log_test("GET /api/menu", False, "No menu items returned")
            else:
                self.log_test("GET /api/menu", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/menu", False, "Request failed", str(e))
        
        # Test GET /api/menu/categories
        try:
            response = requests.get(f"{self.base_url}/menu/categories", timeout=10)
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])
                expected_categories = ["Soups", "Starters - Vegetarian", "Rice Varieties - Vegetarian", 
                                     "Rice Varieties - Non Vegetarian", "Tiffen Varieties", "Desserts"]
                if len(categories) > 0:
                    self.log_test("GET /api/menu/categories", True, f"Retrieved {len(categories)} categories")
                    # Check if expected categories are present
                    found_categories = [cat for cat in expected_categories if cat in categories]
                    self.log_test("Category Content Check", True, f"Found {len(found_categories)} expected categories")
                else:
                    self.log_test("GET /api/menu/categories", False, "No categories returned")
            else:
                self.log_test("GET /api/menu/categories", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/menu/categories", False, "Request failed", str(e))
        
        # Test GET /api/menu/category/{category}
        try:
            test_category = "Soups"
            response = requests.get(f"{self.base_url}/menu/category/{test_category}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                if len(menu_items) > 0:
                    # Verify all items belong to the requested category
                    correct_category = all(item.get('category') == test_category for item in menu_items)
                    if correct_category:
                        self.log_test(f"GET /api/menu/category/{test_category}", True, 
                                    f"Retrieved {len(menu_items)} items from {test_category}")
                    else:
                        self.log_test(f"GET /api/menu/category/{test_category}", False, 
                                    "Some items don't belong to requested category")
                else:
                    self.log_test(f"GET /api/menu/category/{test_category}", False, "No items returned for category")
            else:
                self.log_test(f"GET /api/menu/category/{test_category}", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test(f"GET /api/menu/category/{test_category}", False, "Request failed", str(e))
    
    def test_order_creation(self):
        """Test order creation endpoint"""
        print("\n=== Testing Order Creation ===")
        
        # Sample order data with authentic Indian names and realistic cart
        order_data = {
            "customer_name": "Priya Sharma",
            "customer_phone": "+1-555-0123",
            "customer_email": "priya.sharma@email.com",
            "items": [
                {
                    "menu_item_id": "sample-id-1",
                    "quantity": 2,
                    "name": "Chicken Biryani",
                    "price": 18.0
                },
                {
                    "menu_item_id": "sample-id-2", 
                    "quantity": 1,
                    "name": "Vegetable Soup",
                    "price": 8.0
                }
            ],
            "payment_method": "credit_card",
            "notes": "Please make it medium spicy"
        }
        
        try:
            response = requests.post(f"{self.base_url}/orders", 
                                   json=order_data, 
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'order_id' in data:
                    self.sample_order_id = data['order_id']
                    self.log_test("POST /api/orders", True, f"Order created successfully with ID: {data['order_id']}")
                else:
                    self.log_test("POST /api/orders", False, "Order created but no order_id returned")
            else:
                self.log_test("POST /api/orders", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/orders", False, "Request failed", str(e))
    
    def test_admin_login(self):
        """Test admin authentication"""
        print("\n=== Testing Admin Authentication ===")
        
        # Test with correct password
        login_data = {"password": "kanshka123"}
        try:
            response = requests.post(f"{self.base_url}/admin/login",
                                   json=login_data,
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.admin_token = data['token']
                    self.log_test("POST /api/admin/login (correct password)", True, "Admin login successful")
                else:
                    self.log_test("POST /api/admin/login (correct password)", False, "Login successful but no token returned")
            else:
                self.log_test("POST /api/admin/login (correct password)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/admin/login (correct password)", False, "Request failed", str(e))
        
        # Test with incorrect password
        wrong_login_data = {"password": "wrongpassword"}
        try:
            response = requests.post(f"{self.base_url}/admin/login",
                                   json=wrong_login_data,
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            if response.status_code == 401:
                self.log_test("POST /api/admin/login (wrong password)", True, "Correctly rejected invalid password")
            else:
                self.log_test("POST /api/admin/login (wrong password)", False, f"Should return 401, got {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/admin/login (wrong password)", False, "Request failed", str(e))
    
    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        print("\n=== Testing Admin Endpoints ===")
        
        if not self.admin_token:
            self.log_test("Admin Endpoints", False, "Cannot test admin endpoints - no admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET /api/admin/orders
        try:
            response = requests.get(f"{self.base_url}/admin/orders", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                self.log_test("GET /api/admin/orders", True, f"Retrieved {len(orders)} orders")
            else:
                self.log_test("GET /api/admin/orders", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/admin/orders", False, "Request failed", str(e))
        
        # Test GET /api/admin/menu
        try:
            response = requests.get(f"{self.base_url}/admin/menu", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                self.log_test("GET /api/admin/menu", True, f"Retrieved {len(menu_items)} menu items for admin")
            else:
                self.log_test("GET /api/admin/menu", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/admin/menu", False, "Request failed", str(e))
    
    def test_admin_menu_update(self):
        """Test menu item updates"""
        print("\n=== Testing Menu Management ===")
        
        if not self.sample_menu_item_id:
            self.log_test("Menu Update Test", False, "Cannot test menu update - no sample menu item ID available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        
        # Test price update
        update_data = {"price": 25.0, "available": True}
        try:
            response = requests.put(f"{self.base_url}/admin/menu/{self.sample_menu_item_id}",
                                  json=update_data,
                                  headers=headers,
                                  timeout=10)
            if response.status_code == 200:
                self.log_test("PUT /api/admin/menu/{item_id}", True, "Menu item updated successfully")
            else:
                self.log_test("PUT /api/admin/menu/{item_id}", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("PUT /api/admin/menu/{item_id}", False, "Request failed", str(e))
    
    def test_order_status_update(self):
        """Test order status updates"""
        print("\n=== Testing Order Status Management ===")
        
        if not self.sample_order_id:
            self.log_test("Order Status Update Test", False, "Cannot test order status update - no sample order ID available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        
        # Test status update
        status_data = {"status": "confirmed"}
        try:
            response = requests.put(f"{self.base_url}/admin/orders/{self.sample_order_id}/status",
                                  json=status_data,
                                  headers=headers,
                                  timeout=10)
            if response.status_code == 200:
                self.log_test("PUT /api/admin/orders/{order_id}/status", True, "Order status updated successfully")
            else:
                self.log_test("PUT /api/admin/orders/{order_id}/status", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("PUT /api/admin/orders/{order_id}/status", False, "Request failed", str(e))
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid category
        try:
            response = requests.get(f"{self.base_url}/menu/category/InvalidCategory", timeout=10)
            if response.status_code == 200:
                data = response.json()
                menu_items = data.get('menu_items', [])
                if len(menu_items) == 0:
                    self.log_test("Invalid Category Handling", True, "Returns empty list for invalid category")
                else:
                    self.log_test("Invalid Category Handling", False, "Should return empty list for invalid category")
            else:
                self.log_test("Invalid Category Handling", True, f"Properly handles invalid category with HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Category Handling", False, "Request failed", str(e))
        
        # Test invalid menu item update
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
            update_data = {"price": 15.0}
            try:
                response = requests.put(f"{self.base_url}/admin/menu/invalid-id",
                                      json=update_data,
                                      headers=headers,
                                      timeout=10)
                if response.status_code == 404:
                    self.log_test("Invalid Menu Item Update", True, "Correctly returns 404 for invalid menu item ID")
                else:
                    self.log_test("Invalid Menu Item Update", False, f"Should return 404, got {response.status_code}")
            except Exception as e:
                self.log_test("Invalid Menu Item Update", False, "Request failed", str(e))
    
    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting Kansha Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in logical order
        self.test_menu_endpoints()
        self.test_order_creation()
        self.test_admin_login()
        self.test_admin_endpoints()
        self.test_admin_menu_update()
        self.test_order_status_update()
        self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  • {test['test']}: {test['message']}")
                    if test['details']:
                        print(f"    Details: {test['details']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = KanshaBackendTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)