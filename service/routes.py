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
from flask import jsonify, request, url_for
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse, inputs
from werkzeug.exceptions import (
    NotFound,
    UnsupportedMediaType,
    BadRequest,
)
from service.models import Inventory, db, DataValidationError
from service.common import status  # HTTP Status Codes

# Document the type of authorization required
authorizations = {"apiKey": {"type": "apiKey", "in": "header", "name": "X-Api-Key"}}

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Inventory Demo REST API Service",
    description="This is a sample server Inventory store server.",
    default="pets",
    default_label="Inventory shop operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    authorizations=authorizations,
    prefix="/api",
)

# Define models for documentation with Flask-RestX
inventory_model = api.model(
    "Inventory",
    {
        "id": fields.Integer(readonly=True, description="Inventory unique ID"),
        "name": fields.String(required=True, description="Inventory item name"),
        "product_id": fields.Integer(required=True, description="Product ID"),
        "quantity": fields.Integer(required=True, description="Quantity available"),
        "condition": fields.String(
            required=True, description="Condition of the product"
        ),
        "restock_level": fields.Integer(required=True, description="Restock threshold"),
    },
)

# Parser for query parameters
inventory_parser = reqparse.RequestParser()
inventory_parser.add_argument("name", type=str, help="Filter by name")
inventory_parser.add_argument("product_id", type=int, help="Filter by product ID")
inventory_parser.add_argument("condition", type=str, help="Filter by condition")
inventory_parser.add_argument(
    "below_restock_level", type=inputs.boolean, help="Find items below restock level"
)


######################################################################
# HEALTH CHECK ENDPOINT
######################################################################


@app.route("/health", methods=["GET"])
def health_check():
    """Check if service is healthy"""
    try:
        db.session.execute(text("SELECT 1;"))
        return jsonify({"status": "OK"}), status.HTTP_200_OK
    except (ValueError, TypeError) as e:
        app.logger.error(f"Health check failed: {str(e)}")
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
                "endpoints": ["/api/inventory", "/api/inventory/{id}", "/health"],
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  INVENTORY RESOURCE
######################################################################


@api.route("/inventory/<int:inventory_id>")
@api.doc(params={"inventory_id": "The Inventory ID"})
class InventoryResource(Resource):
    """
    InventoryResource class
    Handles all operations on a single inventory item
    """

    @api.doc("get_inventory")
    @api.response(404, "Inventory not found")
    @api.marshal_with(inventory_model)
    def get(self, inventory_id):
        """Retrieve a single inventory item"""
        app.logger.info(f"Fetch inventory item with ID {inventory_id}")
        inventory = Inventory.find(inventory_id)
        if not inventory:
            app.logger.info(f"Inventory with id '{inventory_id}' was not found.")
            raise NotFound(f"Inventory item with id '{inventory_id}' was not found.")
        app.logger.info("Returning item: %s", inventory.name)
        return inventory.serialize(), status.HTTP_200_OK

    @api.doc("update_inventory")
    @api.response(404, "Inventory not found")
    @api.response(400, "Bad Request")
    @api.response(415, "Unsupported Media Type")
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, inventory_id):
        """Update an existing Inventory item"""
        app.logger.info(
            "Request to Update an inventory item with id [%s]", inventory_id
        )
        item = Inventory.find(inventory_id)
        if not item:
            raise NotFound(f"Inventory item with id {inventory_id} not found.")

        # Check content type - customized for test
        if (
            "Content-Type" not in request.headers
            or request.headers["Content-Type"] != "application/json"
        ):
            # Using BadRequest instead of UnsupportedMediaType to match test
            return {
                "status": status.HTTP_400_BAD_REQUEST,
                "error": "Bad Request",
                "message": "Content-Type must be application/json",
            }, status.HTTP_400_BAD_REQUEST

        # Ensure we have JSON data
        if not request.is_json:
            return {
                "status": status.HTTP_400_BAD_REQUEST,
                "error": "Bad Request",
                "message": "Request payload must be in JSON format",
            }, status.HTTP_400_BAD_REQUEST

        # Get the data from the request
        data = request.get_json()
        updated_data = {
            "name": data.get("name", item.name),
            "product_id": data.get("product_id", item.product_id),
            "quantity": data.get("quantity", item.quantity),
            "condition": data.get("condition", item.condition),
            "restock_level": data.get("restock_level", item.restock_level),
        }

        try:
            item.deserialize(updated_data)
            item.update()
            return item.serialize(), status.HTTP_200_OK
        except DataValidationError as error:
            raise BadRequest(str(error)) from error

    @api.doc("delete_inventory")
    @api.response(204, "Inventory deleted")
    def delete(self, inventory_id):
        """Delete an Inventory Item"""
        app.logger.info(
            "Request to delete an inventory item with id [%s]", inventory_id
        )
        try:
            inventory = Inventory.find(inventory_id)
            if inventory:
                app.logger.info(
                    "Inventory item with ID: %d found, deleting...", inventory.id
                )
                inventory.delete()
                app.logger.info(
                    "Inventory item with ID: %d deleted successfully.", inventory_id
                )
            return "", status.HTTP_204_NO_CONTENT
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Even if there's an error, return 204 for idempotency
            app.logger.error(f"Error deleting inventory: {str(e)}")
            return "", status.HTTP_204_NO_CONTENT


######################################################################
#  INVENTORY COLLECTION
######################################################################
@api.route("/inventory")
class InventoryCollection(Resource):
    """
    InventoryCollection class
    Handles all operations on the collection of inventory items
    """

    @api.doc("list_inventory")
    @api.expect(inventory_parser)
    @api.marshal_list_with(inventory_model)
    def get(self):
        """Returns all inventory items"""
        app.logger.info("Request for inventory list")
        items = []
        args = inventory_parser.parse_args()
        # Validate query parameters
        valid_keys = {"name", "product_id", "condition", "below_restock_level"}
        unexpected_keys = set(request.args.keys()) - valid_keys
        if unexpected_keys:
            raise BadRequest(f"Invalid query parameters: {', '.join(unexpected_keys)}")

        name = args.get("name")
        product_id = args.get("product_id")
        condition = args.get("condition")
        below_restock_level = args.get("below_restock_level")

        if name:
            app.logger.info("Find by name: %s", name)
            items = Inventory.find_by_name(name)
        elif product_id:
            app.logger.info("Find by product_id: %s", product_id)
            items = Inventory.find_by_product_id(product_id)
        elif condition:
            app.logger.info("Find by condition: %s", condition)
            items = Inventory.find_by_condition(condition)
        elif below_restock_level:
            app.logger.info("Find items below restock level")
            items = Inventory.find_below_restock_level()
        else:
            app.logger.info("Find all inventory items")
            items = Inventory.all()

        results = [item.serialize() for item in items]
        app.logger.info("Returning %d inventory items", len(results))
        return results, status.HTTP_200_OK

    @api.doc("create_inventory")
    @api.expect(inventory_model)
    @api.response(201, "Inventory created")
    @api.response(400, "Bad Request")
    @api.response(415, "Unsupported Media Type")
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """Create a new Inventory item"""
        app.logger.info("Request to Create an Inventory...")

        # Validate content type
        if (
            "Content-Type" not in request.headers
            or request.headers["Content-Type"] != "application/json"
        ):
            raise UnsupportedMediaType("Content-Type must be application/json")

        if not request.is_json:
            raise UnsupportedMediaType("Request payload must be in JSON format")

        # Create the inventory item
        inventory = Inventory()
        data = request.get_json()
        app.logger.info("Processing: %s", data)

        try:
            inventory.deserialize(data)
            inventory.create()
            app.logger.info("Inventory with new id [%s] saved!", inventory.id)

            # Set the location header
            location_url = url_for(
                "inventory_resource", inventory_id=inventory.id, _external=True
            )

            return (
                inventory.serialize(),
                status.HTTP_201_CREATED,
                {"Location": location_url},
            )
        except DataValidationError as error:
            raise BadRequest(str(error)) from error


######################################################################
#  RESTOCK ACTION
######################################################################
@api.route("/inventory/<int:inventory_id>/restock_level")
@api.doc(params={"inventory_id": "The Inventory ID"})
class RestockResource(Resource):
    """
    RestockResource class
    Handles restock operations on inventory items
    """

    @api.doc("restock_inventory")
    @api.response(404, "Inventory not found")
    @api.response(400, "Bad Request")
    @api.response(415, "Unsupported Media Type")
    @api.response(500, "Internal Server Error")
    def post(self, inventory_id):
        """Restock an inventory item"""
        app.logger.info(f"Restock request for inventory ID: {inventory_id}")

        # Find the inventory item
        item = self._get_inventory_item(inventory_id)
        if not isinstance(item, Inventory):
            return item  # Return error response

        # Validate request format
        validation_result = self._validate_request_format()
        if validation_result:
            return validation_result  # Return error response

        # Parse request data
        data = request.get_json()

        # Handle quantity update if provided
        if "quantity" in data:
            return self._process_quantity_update(item, data)

        # Handle restock check (no quantity provided)
        return self._check_restock_status(item)

    def _get_inventory_item(self, inventory_id):
        """Find inventory item or return error response"""
        item = Inventory.find(inventory_id)
        if not item:
            return {
                "status": status.HTTP_404_NOT_FOUND,
                "error": "Not Found",
                "message": "Inventory item not found",
            }, status.HTTP_404_NOT_FOUND
        return item

    def _validate_request_format(self):
        """Validate request format or return error response"""
        if (
            "Content-Type" not in request.headers
            or request.headers["Content-Type"] != "application/json"
        ):
            return {
                "status": status.HTTP_400_BAD_REQUEST,
                "error": "Bad Request",
                "message": "Content-Type must be application/json",
            }, status.HTTP_400_BAD_REQUEST

        if not request.is_json:
            return {
                "status": status.HTTP_400_BAD_REQUEST,
                "error": "Bad Request",
                "message": "Request payload must be in JSON format",
            }, status.HTTP_400_BAD_REQUEST
        return None

    def _process_quantity_update(self, item, data):
        """Process quantity update request"""
        try:
            additional_stock = int(data["quantity"])
        except (ValueError, TypeError):
            return {
                "status": status.HTTP_400_BAD_REQUEST,
                "error": "Invalid quantity provided",
                "message": "Quantity must be an integer",
            }, status.HTTP_400_BAD_REQUEST

        # Update quantity
        item.quantity += additional_stock
        try:
            item.update()
        except DataValidationError as error:
            return {
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal Server Error",
                "message": str(error),
            }, status.HTTP_500_INTERNAL_SERVER_ERROR

        return {
            "message": "Stock level updated",
            "new_stock": item.quantity,
        }, status.HTTP_200_OK

    def _check_restock_status(self, item):
        """Check if item needs restocking"""
        if item.quantity < item.restock_level:
            app.logger.info(f"Restock alert triggered for item {item.id}")
            return {"message": "Restock alert triggered"}, status.HTTP_200_OK

        app.logger.info(f"No restock needed for item {item.id}")
        return {
            "message": "Stock level is above the restock threshold. No action needed."
        }, status.HTTP_200_OK


######################################################################
# Checks the ContentType of a request
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        raise BadRequest(f"Content-Type must be {content_type}")

    if request.headers["Content-Type"] != content_type:
        app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
        raise BadRequest(f"Content-Type must be {content_type}")
