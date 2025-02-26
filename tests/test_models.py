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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Inventory, DataValidationError, db
from .factories import InventoryModelFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  YourResourceModel   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestInventoryModel(TestCase):
    """Test Cases for YourResourceModel Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()
        # db.drop_all()
        # db.create_all()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_example_replace_this(self):
        """It should create an Inventory item"""
        resource = InventoryModelFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        found = Inventory.all()
        self.assertEqual(len(found), 1)
        data = Inventory.find(resource.id)
        self.assertEqual(data.name, resource.name)

    def test_serialize_inventory(self):
        """It should serialize an Inventory item into a dictionary"""
        inv = InventoryModelFactory()
        inv.create()
        serial = inv.serialize()
        self.assertIn("id", serial)
        self.assertIn("name", serial)
        self.assertIn("product_id", serial)
        self.assertIn("quantity", serial)
        self.assertIn("condition", serial)
        self.assertIn("restock_level", serial)
        self.assertEqual(serial["product_id"], inv.product_id)
        self.assertEqual(serial["name"], inv.name)

    def test_deserialize_inventory(self):
        """It should deserialize an Inventory item from a dictionary"""
        data = {
            "name": "TestItem",
            "product_id": 1234,
            "quantity": 10,
            "condition": "New",
            "restock_level": 5
        }
        inv = Inventory()
        inv.deserialize(data)
        self.assertEqual(inv.name, "TestItem")
        self.assertEqual(inv.product_id, 1234)
        self.assertEqual(inv.quantity, 10)
        self.assertEqual(inv.condition, "New")
        self.assertEqual(inv.restock_level, 5)

    def test_deserialize_missing_key(self):
        """It should raise DataValidationError when a required field is missing"""
        # Here, "name" is missing intentionally
        data = {
            "product_id": 1234,
            "quantity": 10,
            "condition": "New",
            "restock_level": 5
        }
        inv = Inventory()
        with self.assertRaises(DataValidationError):
            inv.deserialize(data)

    def test_deserialize_bad_type(self):
        """It should raise DataValidationError when passing in bad data"""
        inv = Inventory()
        with self.assertRaises(DataValidationError):
            inv.deserialize("this is not a dictionary")

    def test_update_inventory(self):
        """It should update an existing Inventory record"""
        inv = InventoryModelFactory()
        inv.create()
        self.assertIsNotNone(inv.id)
        original_id = inv.id
        # Change quantity and name
        inv.quantity = 99
        inv.name = "UpdatedName"
        inv.update()
        updated_inv = Inventory.find(original_id)
        self.assertEqual(updated_inv.quantity, 99)
        self.assertEqual(updated_inv.name, "UpdatedName")

    def test_delete_inventory(self):
        """It should delete an Inventory record"""
        inv = InventoryModelFactory()
        inv.create()
        self.assertIsNotNone(inv.id)
        original_id = inv.id
        inv.delete()
        deleted_inv = Inventory.find(original_id)
        self.assertIsNone(deleted_inv)

    def test_find_inventory(self):
        """It should find an Inventory record by ID"""
        inv = InventoryModelFactory()
        inv.create()
        self.assertIsNotNone(inv.id)
        found_inv = Inventory.find(inv.id)
        self.assertEqual(found_inv.id, inv.id)

    def test_find_by_name(self):
        """It should find an Inventory record by name"""
        inv = InventoryModelFactory()
        inv.create()
        self.assertIsNotNone(inv.id)
        found_inv = Inventory.find_by_name(inv.name).first()
        self.assertEqual(found_inv.name, inv.name)

    def test_find_all(self):
        """It should return all Inventory records"""
        inv1 = InventoryModelFactory()
        inv1.create()
        inv2 = InventoryModelFactory()
        inv2.create()
        found = Inventory.all()
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0].name, inv1.name)
        self.assertEqual(found[1].name, inv2.name)

    def test_find_all_empty(self):
        """It should return an empty list when no Inventory records exist"""
        found = Inventory.all()
        self.assertEqual(len(found), 0)

    def test_inventory_schema(self):
        """It should have the expected columns in the Inventory table"""
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns("inventory")
        column_names = [column["name"] for column in columns]
        expected = ["id", "name", "product_id", "quantity", "condition", "restock_level"]
        for col in expected:
            self.assertIn(col, column_names)

    def test_create_inventory_error(self):
        """It should raise DataValidationError when commit fails during create()"""
        inv = InventoryModelFactory()
        original_commit = db.session.commit
        # Force commit to fail by monkey-patching commit

        def failing_commit():
            raise Exception("Forced commit failure")
        db.session.commit = failing_commit
        with self.assertRaises(DataValidationError) as context:
            inv.create()
        self.assertIn("Forced commit failure", str(context.exception))
        # Restore original commit method
        db.session.commit = original_commit

    def test_update_inventory_error(self):
        """It should raise DataValidationError when commit fails during update()"""
        inv = InventoryModelFactory()
        inv.create()
        original_commit = db.session.commit
        # Force commit failure on update

        def failing_commit():
            raise Exception("Forced update failure")
        db.session.commit = failing_commit
        with self.assertRaises(DataValidationError) as context:
            inv.update()
        self.assertIn("Forced update failure", str(context.exception))
        db.session.commit = original_commit

    def test_delete_inventory_error(self):
        """It should raise DataValidationError when commit fails during delete()"""
        inv = InventoryModelFactory()
        inv.create()
        original_commit = db.session.commit
        # Force commit failure on delete

        def failing_commit():
            raise Exception("Forced delete failure")
        db.session.commit = failing_commit
        with self.assertRaises(DataValidationError) as context:
            inv.delete()
        self.assertIn("Forced delete failure", str(context.exception))
        db.session.commit = original_commit
