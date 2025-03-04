"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Inventory as InventoryModel


class InventoryModelFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = InventoryModel

    name = factory.Faker("word")
    product_id = factory.Sequence(lambda n: 1000 + n)
    quantity = 10
    condition = "New"
    restock_level = 5

    # Implementing other attributes here...
