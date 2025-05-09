######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from werkzeug.exceptions import (
    NotFound,
    MethodNotAllowed,
    UnsupportedMediaType,
    BadRequest,
)
from service.common.error_handlers import (
    not_found,
    method_not_allowed,
    unsupported_media_type,
    handle_bad_request,
    handle_data_validation_error,
    handle_unexpected_exceptions,
)
from service.common import status
from service.models import db, Inventory, DataValidationError
from service.routes import check_content_type
from wsgi import app
from .factories import InventoryModelFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/inventory"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_inventory(self) -> Inventory:
        """Helper function to create a single inventory item"""
        test_inventory = InventoryModelFactory()
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Could not create test inventory",
        )
        new_inventory = response.get_json()
        test_inventory.id = new_inventory["id"]
        return test_inventory

    # added more test cases
    def test_method_not_allowed(self):
        """It should return 405 Method Not Allowed"""
        resp = self.client.patch(f"{BASE_URL}/1")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_mediatype_not_supported(self):
        """It should return 415 Unsupported Media Type"""
        test_inventory = InventoryModelFactory()
        resp = self.client.post(
            BASE_URL, data=test_inventory.serialize(), content_type="text/plain"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_internal_server_error(self):
        """It should return 500 Internal Server Error"""
        with patch(
            "service.models.Inventory.find",
            side_effect=Exception("Internal Server Error"),
        ):
            resp = self.client.get(f"{BASE_URL}/1")
            self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    # Implementing test cases here...

    ######################################################################
    # ROOT ENDPOINT TEST CASES
    ######################################################################

    def test_index(self):
        """It should return API metadata from the root endpoint"""
        resp = self.client.get("/metadata")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        metadata = resp.get_json()
        self.assertEqual(metadata["service"], "inventory-service")
        self.assertEqual(metadata["version"], "1.0")
        self.assertIn("/api/inventory", metadata["endpoints"])
        self.assertIn("/api/inventory/{id}", metadata["endpoints"])
        self.assertIn("/health", metadata["endpoints"])

    ######################################################################
    # HEALTH CHECK TEST CASES
    ######################################################################

    def test_health_check(self):
        """It should return service health status"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        health_status = resp.get_json()
        self.assertIn("status", health_status)
        self.assertEqual(health_status["status"], "OK")  # If DB is connected

    ######################################################################
    # LIST INVENTORY TEST CASES
    ######################################################################

    def test_list_inventory(self):
        """It should List all Inventory items"""
        # Ensure there are no items first
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsInstance(data, list)  # Should return a list
        self.assertEqual(len(data), 0)  # Ensure list is empty when no items exist

    def test_list_inventory_with_items(self):
        """It should return all inventory items in the database"""
        for _ in range(3):
            item = InventoryModelFactory()
            item.create()

        # Call GET /inventory
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response contains exactly 3 items
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

    def test_list_inventory_filter_by_name(self):
        """It should return inventory items filtered by name"""

        # Create inventory items
        item1 = InventoryModelFactory(name="Bucket")
        item1.create()
        item2 = InventoryModelFactory(name="Hat")
        item2.create()

        # Call GET /inventory with name filter
        response = self.client.get(BASE_URL, query_string={"name": "Bucket"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response contains only 1 item with name "Widget"
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Bucket")

    def test_list_inventory_filter_by_product_id(self):
        """It should return inventory items filtered by product_id"""

        item1 = InventoryModelFactory(product_id=1001)
        item1.create()
        item2 = InventoryModelFactory(product_id=1002)
        item2.create()

        # Call GET /inventory with product_id filter
        response = self.client.get(BASE_URL, query_string={"product_id": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response contains only one item with product_id 1001
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_id"], 1001)

    def test_list_inventory_filter_by_condition(self):
        """It should return inventory items filtered by condition"""
        # Create inventory items with different conditions
        item1 = InventoryModelFactory(condition="New")
        item1.create()
        item2 = InventoryModelFactory(condition="Used")
        item2.create()

        # Test filtering by "New" condition
        response = self.client.get(BASE_URL, query_string={"condition": "New"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["condition"], "New")

        # Test filtering by "Used" condition
        response = self.client.get(BASE_URL, query_string={"condition": "Used"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["condition"], "Used")

    def test_list_inventory_filter_by_below_restock_level(self):
        """It should return inventory items that need restocking"""
        # Create inventory items with different quantities and restock levels
        item1 = InventoryModelFactory(
            quantity=5, restock_level=10
        )  # Below restock level
        item1.create()
        item2 = InventoryModelFactory(
            quantity=15, restock_level=10
        )  # Above restock level
        item2.create()

        # Test filtering items below restock level
        response = self.client.get(
            BASE_URL, query_string={"below_restock_level": "true"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["quantity"], 5)
        self.assertEqual(data[0]["restock_level"], 10)

    def test_list_inventory_invalid_query_parameter(self):
        """It should return 400 Bad Request for invalid query parameters"""
        response = self.client.get(BASE_URL, query_string={"invalid_param": "value"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid query parameters", response.get_json()["message"])

    ######################################################################
    # READ INVENTORY TEST CASES
    ######################################################################

    def test_get_inventory(self):
        """It should Retrieve an Inventory item by ID"""
        # Create a test inventory item
        test_inventory = self._create_inventory()

        # Fetch the created inventory item
        response = self.client.get(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if response matches created item
        data = response.get_json()
        self.assertEqual(data["id"], test_inventory.id)

    ######################################################################
    # CREATE INVENTORY TEST CASES
    ######################################################################

    def test_create_inventory(self):
        """It should Create a new Inventory"""
        test_inventory = InventoryModelFactory()
        logging.debug("Test Inventory: %s", test_inventory.serialize())
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_inventory = response.get_json()
        self.assertEqual(new_inventory["name"], test_inventory.name)
        self.assertEqual(new_inventory["product_id"], test_inventory.product_id)
        self.assertEqual(new_inventory["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory["condition"], test_inventory.condition)
        self.assertEqual(new_inventory["restock_level"], test_inventory.restock_level)

        # have uncommented the code below as get inventory is implemented
        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_inventory = response.get_json()
        self.assertEqual(new_inventory["name"], test_inventory.name)
        self.assertEqual(new_inventory["product_id"], test_inventory.product_id)
        self.assertEqual(new_inventory["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory["condition"], test_inventory.condition)
        self.assertEqual(new_inventory["restock_level"], test_inventory.restock_level)

    # ######################################################################
    # # UPDATE INVENTORY TEST CASES
    # ######################################################################
    def test_update_inventory_success(self):
        """It should update an existing Inventory item successfully."""
        new_item = {
            "name": "OriginalName",
            "product_id": 111,
            "quantity": 5,
            "condition": "New",
            "restock_level": 3,
        }
        create_resp = self.client.post("/api/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_data = {
            "name": "UpdatedName",
            "quantity": 10,
            "condition": "Used",
            "restock_level": 2,
        }
        update_resp = self.client.put(f"/api/inventory/{item_id}", json=update_data)
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)
        updated_item = update_resp.get_json()
        self.assertEqual(updated_item["name"], "UpdatedName")
        self.assertEqual(updated_item["quantity"], 10)
        self.assertEqual(updated_item["condition"], "Used")
        self.assertEqual(updated_item["restock_level"], 2)

    def test_update_inventory_not_found(self):
        """It should return 404 when updating a non-existent item."""
        update_data = {"name": "NonExistent", "quantity": 5}
        resp = self.client.put("/inventory/9999", json=update_data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_invalid_data(self):
        """It should return 400 when updating with invalid data (negative quantity)."""
        new_item = {
            "name": "TestItem",
            "product_id": 222,
            "quantity": 5,
            "condition": "New",
            "restock_level": 3,
        }
        create_resp = self.client.post("/api/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_data = {"quantity": -10}
        update_resp = self.client.put(f"/api/inventory/{item_id}", json=update_data)
        self.assertEqual(update_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory_invalid_condition(self):
        """It should return 400 when updating with an invalid condition."""
        new_item = {
            "name": "TestItem",
            "product_id": 333,
            "quantity": 5,
            "condition": "New",
            "restock_level": 3,
        }
        create_resp = self.client.post("/api/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_data = {"condition": "InvalidCondition"}
        update_resp = self.client.put(f"/api/inventory/{item_id}", json=update_data)
        self.assertEqual(update_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory_invalid_restock_level(self):
        """It should return 400 when updating with an invalid restock_level (negative)."""
        new_item = {
            "name": "TestItem",
            "product_id": 444,
            "quantity": 5,
            "condition": "New",
            "restock_level": 3,
        }
        create_resp = self.client.post("/api/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_data = {"restock_level": -5}
        update_resp = self.client.put(f"/api/inventory/{item_id}", json=update_data)
        self.assertEqual(update_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory_non_json(self):
        """It should return 400 when payload is not JSON."""
        new_item = {
            "name": "TestItem",
            "product_id": 555,
            "quantity": 5,
            "condition": "New",
            "restock_level": 3,
        }
        create_resp = self.client.post("/api/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_resp = self.client.put(
            f"/api/inventory/{item_id}", data="not json", content_type="text/plain"
        )
        self.assertEqual(update_resp.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    # DELETE INVENTORY TEST CASES
    ######################################################################
    def test_delete_inventory(self):
        """It should Delete an Inventory item"""
        # Create an inventory item to delete
        test_inventory = self._create_inventory()
        response = self.client.delete(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # Check that the item is deleted
        response = self.client.get(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_inventory(self):
        """It should return 204 when trying to delete a non-existing item"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)  # Ensure no content is returned

    ######################################################################
    # Restock Alert and Update Restock Level Test Cases
    ######################################################################

    def test_restock_item_not_found(self):
        """It should return 404 if the inventory item doesn't exist"""
        resp = self.client.post(
            "/api/inventory/9999/restock_level", json={"quantity": 5}
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertIn("Inventory item not found", data["message"])

    def test_restock_not_json(self):
        """It should return 400 if the payload is not JSON"""
        test_inventory = self._create_inventory()
        resp = self.client.post(
            f"/api/inventory/{test_inventory.id}/restock_level",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restock_invalid_quantity_value(self):
        """It should return 400 if 'quantity' cannot be parsed as an integer"""
        test_inventory = self._create_inventory()
        resp = self.client.post(
            f"/api/inventory/{test_inventory.id}/restock_level",
            json={"quantity": "ten"},  # not an integer
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertIn("Invalid quantity provided", data["error"])

    @patch(
        "service.models.Inventory.update",
        side_effect=DataValidationError("Forced update failure"),
    )
    def test_restock_forced_500(self, _):
        """It should return 500 Internal Server Error if update fails unexpectedly"""
        test_inventory = self._create_inventory()
        resp = self.client.post(
            f"/api/inventory/{test_inventory.id}/restock_level", json={"quantity": 5}
        )
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = resp.get_json()
        self.assertIn("Forced update failure", data["message"])

    def test_restock_auto_update(self):
        """It should update the stock level when 'quantity' is provided"""
        test_inventory = self._create_inventory()
        # Force known quantity to 15
        update_data = {"quantity": 15, "restock_level": 10}
        update_resp = self.client.put(
            f"/api/inventory/{test_inventory.id}", json=update_data
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        # Now add 27 more
        resp = self.client.post(
            f"/api/inventory/{test_inventory.id}/restock_level", json={"quantity": 27}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["message"], "Stock level updated")
        self.assertEqual(data["new_stock"], 15 + 27)

    # def test_restock_alert_triggered(self):
    #     """It should trigger a restock alert if stock is below restock_level and no quantity is provided"""
    #     test_inventory = self._create_inventory()
    #     # Force quantity to 0, restock_level to 10 so it's below threshold
    #     update_data = {"quantity": 0, "restock_level": 10}
    #     update_resp = self.client.put(
    #         f"/api/inventory/{test_inventory.id}", json=update_data
    #     )
    #     self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

    #     # No quantity in POST, should trigger alert
    #     resp = self.client.post(
    #         f"/api/inventory/{test_inventory.id}/restock_level", json={}
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     data = resp.get_json()
    #     self.assertEqual(data["message"], "Restock alert triggered")
    def test_restock_alert_triggered(self):
        """It should automatically restock if stock is below restock_level and no quantity is provided"""
        test_inventory = self._create_inventory()
        # Force quantity to 0, restock_level to 10 so it's below threshold
        update_data = {"quantity": 0, "restock_level": 10}
        update_resp = self.client.put(
            f"/api/inventory/{test_inventory.id}", json=update_data
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        # No quantity in POST, should trigger auto-restock
        resp = self.client.post(
            f"/api/inventory/{test_inventory.id}/restock_level", json={}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["message"], "Stock level updated to restock level")
        self.assertEqual(
            data["new_stock"], 10
        )  # Verify quantity was updated to restock level

    def test_restock_no_action_needed(self):
        """It should return a 'no action needed' message if stock is above restock_level"""
        test_inventory = self._create_inventory()
        # Force quantity above restock_level
        update_data = {"quantity": 20, "restock_level": 10}
        update_resp = self.client.put(
            f"/api/inventory/{test_inventory.id}", json=update_data
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        # No quantity in POST, should say no action is needed
        resp = self.client.post(
            f"/api/inventory/{test_inventory.id}/restock_level", json={}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(
            data["message"],
            "Stock level is above the restock threshold. No action needed.",
        )

    def test_check_content_type_correct(self):
        """It should pass check_content_type if Content-Type is correct."""
        with app.test_request_context(
            "/api/inventory",
            method="POST",
            headers={"Content-Type": "application/json"},
        ):
            check_content_type("application/json")

    # Add these tests to test_routes.py

    # Add these as methods inside the TestYourResourceService class

    def test_error_handlers_coverage(self):
        """Test coverage for error handlers"""

        # Test NotFound handler
        _, status_code = not_found(NotFound("Not found test"))
        self.assertEqual(status_code, 404)

        # Test MethodNotAllowed handler
        _, status_code = method_not_allowed(MethodNotAllowed("GET", ["POST"]))
        self.assertEqual(status_code, 405)

        # Test UnsupportedMediaType handler
        _, status_code = unsupported_media_type(
            UnsupportedMediaType("Unsupported media")
        )
        self.assertEqual(status_code, 415)

        # Test BadRequest handler
        _, status_code = handle_bad_request(BadRequest("Bad request test"))
        self.assertEqual(status_code, 400)

        # Test DataValidationError handler
        _, status_code = handle_data_validation_error(
            DataValidationError("Data validation error")
        )
        self.assertEqual(status_code, 400)

        # Test unexpected exception handler
        _, status_code = handle_unexpected_exceptions(Exception("Unexpected error"))
        self.assertEqual(status_code, 500)

    def test_routes_coverage(self):
        """Test coverage for routes.py"""

        # Test delete with exception
        with patch(
            "service.models.Inventory.find", side_effect=Exception("Test exception")
        ):
            resp = self.client.delete(f"{BASE_URL}/999")
            self.assertEqual(resp.status_code, 204)

        # Test invalid update request
        item = self._create_inventory()
        resp = self.client.put(
            f"{BASE_URL}/{item.id}",
            headers={},
            data="invalid data",  # Missing Content-Type
        )
        self.assertEqual(resp.status_code, 400)

        # Test restock with exception
        with patch(
            "service.models.Inventory.find", return_value=InventoryModelFactory()
        ):
            with patch(
                "service.models.Inventory.update", side_effect=Exception("Update error")
            ):
                resp = self.client.post(
                    f"{BASE_URL}/{999}/restock_level",
                    json={"quantity": 5},
                    content_type="application/json",
                )
                self.assertEqual(resp.status_code, 500)

    def test_additional_coverage(self):
        """Test coverage for uncovered lines in routes.py"""

        # Test health_check error handling (lines 90-92)
        with patch(
            "service.routes.db.session.execute", side_effect=ValueError("DB Error")
        ):
            resp = self.client.get("/health")
            self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(resp.get_json()["status"], "ERROR")

        # Test put method content type validation (lines 154, 170)
        item = self._create_inventory()
        resp = self.client.put(
            f"{BASE_URL}/{item.id}", headers={}, data="not json"  # Missing Content-Type
        )
        self.assertEqual(resp.status_code, 400)

        # Test post method content type validation (line 284)
        resp = self.client.post(
            BASE_URL, headers={}, data="not json"  # Missing Content-Type
        )
        self.assertEqual(resp.status_code, 415)

        # Test _get_inventory_item (lines 306-307)
        resp = self.client.post(
            f"{BASE_URL}/999999/restock_level",
            json={"quantity": 5},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

        # Test _process_quantity_update exception (line 374)
        with patch(
            "service.models.Inventory.find", return_value=InventoryModelFactory()
        ):
            with patch(
                "service.models.Inventory.update",
                side_effect=DataValidationError("Update error"),
            ):
                resp = self.client.post(
                    f"{BASE_URL}/1/restock_level",
                    json={"quantity": 5},
                    content_type="application/json",
                )
                self.assertEqual(resp.status_code, 500)

        # Test check_content_type function (lines 428-433)
        with app.test_request_context(headers={}):  # No Content-Type header
            with self.assertRaises(BadRequest):
                check_content_type("application/json")

        with app.test_request_context(
            headers={"Content-Type": "text/plain"}
        ):  # Wrong Content-Type
            with self.assertRaises(BadRequest):
                check_content_type("application/json")

    def test_final_coverage_push(self):
        """Test to catch the remaining uncovered lines in coverage tests"""

        # Content-Type missing in PUT
        item = self._create_inventory()
        resp = self.client.put(
            f"{BASE_URL}/{item.id}",
            data="not json",
            # Deliberately omit Content-Type header
        )
        self.assertEqual(resp.status_code, 400)

        # Line 170: PUT with wrong content type
        resp = self.client.put(
            f"{BASE_URL}/{item.id}",
            data="not json",
            headers={"Content-Type": "text/plain"},
        )
        self.assertEqual(resp.status_code, 400)

        # POST with missing Content-Type
        test_data = {"name": "Coverage Test", "product_id": 999, "condition": "New"}
        resp = self.client.post(
            BASE_URL,
            data=str(test_data),
            # Deliberately omit Content-Type header
        )
        self.assertEqual(resp.status_code, 415)

        # RestockResource _validate_request_format
        item = self._create_inventory()
        resp = self.client.post(
            f"{BASE_URL}/{item.id}/restock_level",
            # Deliberately send without Content-Type header
        )
        self.assertEqual(resp.status_code, 400)

        # Test different branches of check_content_type
        with app.test_request_context(headers={}):
            try:
                check_content_type("application/json")
            except BadRequest as e:
                self.assertIn("must be application/json", str(e))

    def test_exact_coverage(self):
        """Test specifically targeting exact line numbers reported by codecov"""

        # Direct test of line 154 (Content-Type check in PUT)
        item = self._create_inventory()
        headers = {}  # Explicitly empty headers to ensure no Content-Type
        resp = self.client.put(f"{BASE_URL}/{item.id}", headers=headers, data="{}")
        self.assertEqual(resp.status_code, 400)

        # Direct test of line 170 (JSON validation in PUT)
        resp = self.client.put(
            f"{BASE_URL}/{item.id}",
            headers={"Content-Type": "application/json"},
            data="This is not JSON",  # Not properly formatted JSON
        )
        self.assertEqual(resp.status_code, 400)

        # Direct test of line 284 (UnsupportedMediaType in POST)
        # Try without ANY headers to ensure hit this code path
        resp = self.client.post(BASE_URL, headers=None, data="{}")
        self.assertEqual(resp.status_code, 415)

        # Direct test of lines 306-307 (_get_inventory_item in RestockResource)
        # Test with a non-existent ID to ensure we hit the not found path
        resp = self.client.post(
            f"{BASE_URL}/99999999/restock_level",
            json={"quantity": 5},
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 404)

        # Direct test of line 374 (Exception in _process_quantity_update)
        # Create an item and then force an update error
        item = self._create_inventory()
        with patch(
            "service.models.Inventory.update",
            side_effect=DataValidationError("Test error"),
        ):
            resp = self.client.post(
                f"{BASE_URL}/{item.id}/restock_level",
                json={"quantity": 5},
                headers={"Content-Type": "application/json"},
            )
            self.assertEqual(resp.status_code, 500)
            self.assertIn("Test error", resp.get_json().get("message", ""))

    @patch(
        "service.models.Inventory.update",
        side_effect=DataValidationError("forced failure"),
    )
    def test_restock_update_failure(self, _):
        """Test restocking when update fails to hit error block for coverage"""
        # Create inventory item
        response = self.client.post(
            BASE_URL,
            json={
                "name": "Test Product",
                "product_id": 9999,
                "quantity": 1,
                "condition": "New",
                "restock_level": 5,
            },
        )
        self.assertEqual(response.status_code, 201)
        item_id = response.get_json()["id"]

        # Force update failure
        response = self.client.post(
            f"{BASE_URL}/{item_id}/restock_level",
            json={},
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("forced failure", response.get_json().get("message", ""))

    def test_create_inventory_page(self):
        """It should render the create inventory form page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            b"Create, Retrieve, Update, and Delete Inventory Items:", response.data
        )
