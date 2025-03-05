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
from wsgi import app
from service.common import status
from service.models import db, Inventory
from .factories import InventoryModelFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory"


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
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        metadata = resp.get_json()
        self.assertEqual(metadata["service"], "inventory-service")
        self.assertEqual(metadata["version"], "1.0")
        self.assertIn("/inventory", metadata["endpoints"])
        self.assertIn("/inventory/{id}", metadata["endpoints"])
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
        create_resp = self.client.post("/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_data = {
            "name": "UpdatedName",
            "quantity": 10,
            "condition": "Used",
            "restock_level": 2,
        }
        update_resp = self.client.put(f"/inventory/{item_id}", json=update_data)
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
        create_resp = self.client.post("/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_data = {"quantity": -10}
        update_resp = self.client.put(f"/inventory/{item_id}", json=update_data)
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
        create_resp = self.client.post("/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_data = {"condition": "InvalidCondition"}
        update_resp = self.client.put(f"/inventory/{item_id}", json=update_data)
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
        create_resp = self.client.post("/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_data = {"restock_level": -5}
        update_resp = self.client.put(f"/inventory/{item_id}", json=update_data)
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
        create_resp = self.client.post("/inventory", json=new_item)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        update_resp = self.client.put(
            f"/inventory/{item_id}", data="not json", content_type="text/plain"
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
        """It should return 404 when trying to delete a non-existing item"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.get_json())
