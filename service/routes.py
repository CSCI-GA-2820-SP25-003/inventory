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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""
from sqlalchemy import text
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Inventory, db, DataValidationError
from service.common import status  # HTTP Status Codes

######################################################################
# HEALTH CHECK INVENTORY
######################################################################


@app.route("/health", methods=["GET"])
def health_check():
    """Check if service is healthy"""
    try:
        db.session.execute(text("SELECT 1;"))
        return jsonify({"status": "OK"}), status.HTTP_200_OK
    except (ValueError, TypeError) as e:
        return (
            jsonify({"status": "ERROR", "message": str(e)}),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Root URL response with service metadata"""
    return (
        jsonify(
            {
                "service": "inventory-service",
                "version": "1.0",
                "endpoints": ["/inventory", "/inventory/{id}", "/health"],
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Implementing REST API code here ...

######################################################################
# LIST INVENTORY
######################################################################


@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all inventory items"""
    app.logger.info("Request for inventory list")

    items = []

    # Parse any arguments from the query string
    name = request.args.get("name")
    product_id = request.args.get("product_id")
    condition = request.args.get("condition")
    below_restock_level = request.args.get("below_restock_level")

    # Validate query parameters
    valid_params = {"name", "product_id", "condition", "below_restock_level"}
    invalid_params = set(request.args.keys()) - valid_params
    if invalid_params:
        app.logger.error("Invalid query parameters: %s", invalid_params)
        return jsonify({"error": f"Invalid query parameters: {invalid_params}"}), status.HTTP_400_BAD_REQUEST

    if name:
        app.logger.info("Find by name: %s", name)
        items = Inventory.find_by_name(name)
    elif product_id:
        app.logger.info("Find by product_id: %s", product_id)
        items = Inventory.find_by_product_id(int(product_id))
    elif condition:
        app.logger.info("Find by condition: %s", condition)
        items = Inventory.find_by_condition(condition)
    elif below_restock_level and below_restock_level.lower() == "true":
        app.logger.info("Find items below restock level")
        items = Inventory.find_below_restock_level()
    else:
        app.logger.info("Find all inventory items")
        items = Inventory.all()

    results = [item.serialize() for item in items]
    app.logger.info("Returning %d inventory items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ INVENTORY
######################################################################


@app.route("/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    """Minimal implementation: Retrieve a single inventory item"""
    app.logger.info(f"Fetch inventory item with ID {inventory_id}")

    inventory = Inventory.find(inventory_id)
    if not inventory:
        return jsonify({"error": "Inventory item not found"}), status.HTTP_404_NOT_FOUND
    app.logger.info("Returning item: %s", inventory.name)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


# CREATE INVENTORY
######################################################################


@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Create a Inventory
    This endpoint will create a Inventory based the data in the body that is posted
    """
    app.logger.info("Request to Create a Inventory...")
    check_content_type("application/json")

    inventory = Inventory()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    inventory.deserialize(data)

    # Save the new Inventory to the database
    inventory.create()
    app.logger.info("Inventory with new id [%s] saved!", inventory.id)

    # Return the location of the new Inventory
    # get_inventory is implemented
    location_url = url_for("get_inventory", inventory_id=inventory.id, _external=True)
    # location_url = "/"

    return (
        jsonify(inventory.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


# ######################################################################
# # UPDATE INVENTORY
# ######################################################################


@app.route("/inventory/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    """
    Update an existing Inventory item.

    This endpoint will:
      1) Find an existing Inventory item by `inventory_id`.
      2) Merge any provided fields (like `name`, `quantity`, etc.)
         with the existing values.
      3) Validate the merged data via `item.deserialize(...)`.
      4) Update the database record if valid, or return 400 if invalid.

    Returns:
      A JSON representation of the updated Inventory item, or
      404 if the item does not exist, or 400 if validation fails.
    """
    item = Inventory.find(inventory_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Inventory item with id {inventory_id} not found.")
    if not request.is_json:
        abort(status.HTTP_400_BAD_REQUEST, "Request payload must be in JSON format")
    data = request.get_json()

    # Merge the incoming update with existing fields
    updated_data = {
        "name": data.get("name", item.name),
        "product_id": data.get("product_id", item.product_id),
        "quantity": data.get("quantity", item.quantity),
        "condition": data.get("condition", item.condition),
        "restock_level": data.get("restock_level", item.restock_level),
    }

    try:
        item.deserialize(updated_data)
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

    item.update()
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# DELETE INVENTORY
######################################################################


@app.route("/inventory/<int:inventory_id>", methods=["DELETE"])
def delete_inventory(inventory_id):
    """
    Delete an Inventory Item
    This endpoint will delete an Inventory Item based on its id
    """
    app.logger.info("Request to delete an inventory item with id [%s]", inventory_id)

    # Find the Inventory item
    inventory = Inventory.find(inventory_id)
    if inventory:
        app.logger.info("Inventory item with ID: %d found, deleting...", inventory.id)
        inventory.delete()
        app.logger.info(
            "Inventory item with ID: %d deleted successfully.", inventory_id
        )
    else:
        app.logger.warning(
            "Inventory item with ID: %d not found. DELETE is idempotent, so returning 204_NO_CONTENT.",
            inventory_id,
        )

    return "", status.HTTP_204_NO_CONTENT

######################################################################
# Restock Alert and Stock Update
######################################################################


@app.route("/inventory/<int:inventory_id>/restock_level", methods=["POST"])
def restock_inventory(inventory_id):
    """
    Trigger a restock alert or update stock levels for an inventory item.

    If a 'quantity' is provided in the JSON payload, update the stock level.
    Otherwise, check if the current stock is below the restock threshold:
      - If below threshold, trigger a restock alert.
      - If not, return a message that no action is needed.

    Returns:
      JSON response confirming the action or alert, or an error if the item is not found.
    """
    # Validate the inventory item exists
    item = Inventory.find(inventory_id)
    if not item:
        return jsonify({"error": "Inventory item not found"}), status.HTTP_404_NOT_FOUND

    if not request.is_json:
        abort(status.HTTP_400_BAD_REQUEST, "Request payload must be in JSON format")
    data = request.get_json()

    # If quantity is provided, update the stock level
    if "quantity" in data:
        try:
            additional_stock = int(data["quantity"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid quantity provided"}), status.HTTP_400_BAD_REQUEST

        item.quantity += additional_stock
        try:
            item.update()
        except DataValidationError as error:
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR, str(error))

        # Re-fetch the item from the database to ensure we have the updated value
        updated_item = Inventory.find(item.id)
        return jsonify({
            "message": "Stock level updated",
            "new_stock": updated_item.quantity
        }), status.HTTP_200_OK

    # If no quantity provided, check if stock is below restock threshold
    if item.quantity < item.restock_level:
        # Trigger a restock alert (here we simply return a message)
        return jsonify({"message": "Restock alert triggered"}), status.HTTP_200_OK
    return jsonify({"message": "Stock level is above the restock threshold. No action needed."}), status.HTTP_200_OK

######################################################################
# Checks the ContentType of a request
######################################################################


def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
