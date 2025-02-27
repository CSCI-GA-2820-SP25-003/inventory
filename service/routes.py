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

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Inventory
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Root URL response with service details"""
    return jsonify({
        "service": "Inventory Management API",
        "version": "1.0",
        "status": "running",
        "description": "A REST API for managing inventory items.",
    }), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...

######################################################################

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
    # Todo: uncomment this code when get_inventory is implemented 
    # location_url = url_for("get_inventory", inventory_id=inventory.id, _external=True)
    location_url = "/"
    
    return jsonify(inventory.serialize()), status.HTTP_201_CREATED, {"Location": location_url}

# DELETE INVENTORY
######################################################################
#@app.route("/inventory/<int:inventory_id>", methods=["DELETE"])
# def delete_inventory(inventory_id):
#     """
#     Delete an Inventory Item

#     This endpoint will delete an Inventory Item based the id specified in the path
#     """
#     app.logger.info("Request to Delete an Inventory item with id [%s]", inventory_id)

#     # Delete the Inventory if it exists
#     inventory = Inventory.find(inventory_id)
#     if inventory:
#         app.logger.info("Inventory with ID: %d found.", inventory.id)
#         inventory.delete()

#     app.logger.info("Inventory with ID: %d delete complete.", inventory_id)
#     return {}, status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE INVENTORY
######################################################################

# @app.route("/inventory/<int:inventory_id>", methods=["PUT"])
# def update_inventory(inventory_id):
#     """
#     Update an existing Inventory item.
#     Expected JSON payload may include any or all of:
#       - name (string)
#       - product_id (int)
#       - quantity (int, non-negative)
#       - condition (one of ["New", "Used", "Open-Box"])
#       - restock_level (int, non-negative)
#     Returns:
#       - 404 if the item doesn't exist.
#       - 400 if the JSON payload is invalid.
#       - 200 with the updated item in JSON if successful.
#     """
#     # Retrieve the Inventory item by ID.
#     item = Inventory.find(inventory_id)
#     if not item:
#         abort(status.HTTP_404_NOT_FOUND, f"Inventory item with id {inventory_id} not found.")

#     # Ensure the request has JSON content.
#     if not request.is_json:
#         abort(status.HTTP_400_BAD_REQUEST, "Request payload must be in JSON format")
#     data = request.get_json()

#     # Helper function to update a field if present, with optional validation.
#     def update_field(field, validator=None, error_msg="Invalid data"):
#         if field in data:
#             value = data[field]
#             if validator and not validator(value):
#                 abort(status.HTTP_400_BAD_REQUEST, error_msg)
#             setattr(item, field, value)

#     update_field("name")
#     update_field("product_id")
#     update_field("quantity", lambda v: isinstance(v, int) and v >= 0,
#                  "Invalid quantity; must be a non-negative integer")
#     update_field("condition", lambda v: v in ["New", "Used", "Open-Box"],
#                  "Invalid condition. Must be one of ['New', 'Used', 'Open-Box']")
#     update_field("restock_level", lambda v: isinstance(v, int) and v >= 0,
#                  "Invalid restock_level; must be a non-negative integer")

#     # Commit changes
#     item.update()

#     # Return updated item
#     return jsonify(item.serialize()), status.HTTP_200_OK


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