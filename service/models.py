"""
Models for YourResourceModel

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class Inventory(db.Model):
    """
    Class that represents an Inventory item
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    condition = db.Column(db.String(63), nullable=False)
    restock_level = db.Column(db.Integer, default=10)

    def __repr__(self):
        return f"<Inventory {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates an Inventory item in the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # Ensure the ID is unset so a new one is generated
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates an Inventory item in the database
        """
        logger.info("Updating %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an Inventory item from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes an Inventory item into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "condition": self.condition,
            "restock_level": self.restock_level,
        }

    def deserialize(self, data):
        """
        Deserializes an Inventory item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            # Validate required fields
            self.name = data["name"]
            self.product_id = data["product_id"]
            self.condition = data["condition"]

            self.name = data["name"]
            if len(self.name) > 63:
                raise DataValidationError("Name exceeds 63-character limit")
            # Validate quantity
            self.quantity = data.get("quantity", 0)
            if self.quantity < 0:
                raise DataValidationError("Quantity cannot be negative")
            # Validate restock level
            self.restock_level = data.get("restock_level", 10)
            if self.restock_level < 0:
                raise DataValidationError("Restock level cannot be negative")
            # Validate condition values
            valid_conditions = ["New", "Opened", "Used", "Refurbished"]
            if self.condition not in valid_conditions:
                raise DataValidationError(f"Invalid condition: {self.condition}")
        except (KeyError, AttributeError, TypeError) as error:
            raise DataValidationError("Invalid inventory data") from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all Inventory items in the database"""
        logger.info("Processing all Inventory items")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds an Inventory item by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_product_id(cls, product_id):
        """Returns all Inventory items with the given product_id"""
        logger.info("Processing product_id query for %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Inventory items with the given name

        Args:
            name (string): the name of the Inventory items you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_condition(cls, condition):
        """Returns all Inventory items with the given condition

        Args:
            condition (string): the condition of the Inventory items you want to match
        """
        logger.info("Processing condition query for %s ...", condition)
        return cls.query.filter(cls.condition == condition)

    @classmethod
    def find_below_restock_level(cls):
        """Returns all Inventory items that need restocking (quantity below restock_level)"""
        logger.info("Processing below restock level query ...")
        return cls.query.filter(cls.quantity < cls.restock_level)


# @classmethod
# def find_by_condition(cls, condition):
#     """Find inventory items by their condition

#     Args:
#         condition (str): The condition to filter by (New, Used, Opened, Refurbished)

#     Returns:
#         list: A list of Inventory items matching the condition
#     """
#     return cls.query.filter(cls.condition == condition).all()
