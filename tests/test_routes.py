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
from wsgi import app
from service.common import status
from service.models import db, Inventory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/delete"


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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...
     # ----------------------------------------------------------
    # DELETE INVENTORY TEST CASES
    # ----------------------------------------------------------
    # def test_delete_inventory(self):
    #     """It should Delete an Inventory Item"""
    #     test_inventory = self._create_inventory(1)[0]
    #     response = self.client.delete(f"{BASE_URL}/{test_inventory.id}")
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(len(response.data), 0)
    #     # make sure they are deleted
    #     response = self.client.get(f"{BASE_URL}/{test_inventory.id}")
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_delete_non_existing_inventory(self):
    #     """It should Delete an inventory even if it doesn't exist"""
    #     response = self.client.delete(f"{BASE_URL}/0")
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(len(response.data), 0)

######################################################################
# UPDATE INVENTORY TEST CASES
######################################################################
    # def test_update_inventory_success(self):
    #     """It should update an existing Inventory item successfully."""
    #     new_item = {
    #         "name": "OriginalName",
    #         "product_id": 111,
    #         "quantity": 5,
    #         "condition": "New",
    #         "restock_level": 3
    #     }
    #     create_resp = self.client.post("/inventory", json=new_item)
    #     self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
    #     item_id = create_resp.get_json()["id"]

    #     update_data = {
    #         "name": "UpdatedName",
    #         "quantity": 10,
    #         "condition": "Used",
    #         "restock_level": 2
    #     }
    #     update_resp = self.client.put(f"/inventory/{item_id}", json=update_data)
    #     self.assertEqual(update_resp.status_code, status.HTTP_200_OK)
    #     updated_item = update_resp.get_json()
    #     self.assertEqual(updated_item["name"], "UpdatedName")
    #     self.assertEqual(updated_item["quantity"], 10)
    #     self.assertEqual(updated_item["condition"], "Used")
    #     self.assertEqual(updated_item["restock_level"], 2)

    # def test_update_inventory_not_found(self):
    #     """It should return 404 when updating a non-existent item."""
    #     update_data = {
    #         "name": "NonExistent",
    #         "quantity": 5
    #     }
    #     resp = self.client.put("/inventory/9999", json=update_data)
    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # def test_update_inventory_invalid_data(self):
    #     """It should return 400 when updating with invalid data (negative quantity)."""
    #     new_item = {
    #         "name": "TestItem",
    #         "product_id": 222,
    #         "quantity": 5,
    #         "condition": "New",
    #         "restock_level": 3
    #     }
    #     create_resp = self.client.post("/inventory", json=new_item)
    #     self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
    #     item_id = create_resp.get_json()["id"]

    #     update_data = {"quantity": -10}
    #     update_resp = self.client.put(f"/inventory/{item_id}", json=update_data)
    #     self.assertEqual(update_resp.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_update_inventory_invalid_condition(self):
    #     """It should return 400 when updating with an invalid condition."""
    #     new_item = {
    #         "name": "TestItem",
    #         "product_id": 333,
    #         "quantity": 5,
    #         "condition": "New",
    #         "restock_level": 3
    #     }
    #     create_resp = self.client.post("/inventory", json=new_item)
    #     self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
    #     item_id = create_resp.get_json()["id"]

    #     update_data = {"condition": "InvalidCondition"}
    #     update_resp = self.client.put(f"/inventory/{item_id}", json=update_data)
    #     self.assertEqual(update_resp.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_update_inventory_invalid_restock_level(self):
    #     """It should return 400 when updating with an invalid restock_level (negative)."""
    #     new_item = {
    #         "name": "TestItem",
    #         "product_id": 444,
    #         "quantity": 5,
    #         "condition": "New",
    #         "restock_level": 3
    #     }
    #     create_resp = self.client.post("/inventory", json=new_item)
    #     self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
    #     item_id = create_resp.get_json()["id"]

    #     update_data = {"restock_level": -5}
    #     update_resp = self.client.put(f"/inventory/{item_id}", json=update_data)
    #     self.assertEqual(update_resp.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_update_inventory_non_json(self):
    #     """It should return 400 when payload is not JSON."""
    #     new_item = {
    #         "name": "TestItem",
    #         "product_id": 555,
    #         "quantity": 5,
    #         "condition": "New",
    #         "restock_level": 3
    #     }
    #     create_resp = self.client.post("/inventory", json=new_item)
    #     self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
    #     item_id = create_resp.get_json()["id"]

    #     update_resp = self.client.put(f"/inventory/{item_id}", data="not json", content_type="text/plain")
    #     self.assertEqual(update_resp.status_code, status.HTTP_400_BAD_REQUEST)
