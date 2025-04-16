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

    name = factory.Faker("pystr", max_chars=63)
    product_id = factory.Sequence(lambda n: 1000 + n)
    quantity = factory.Faker("pyint", min_value=0, max_value=100)
    condition = factory.Faker(
        "random_element", elements=["New", "Opened", "Used", "Refurbished"]
    )
    restock_level = factory.Faker("pyint", min_value=5, max_value=20)

    # Implementing other attributes here...
