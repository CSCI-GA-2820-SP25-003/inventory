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
Module: error_handlers
"""
from flask import jsonify
from flask import current_app as app  # Import Flask application
from werkzeug.exceptions import (
    NotFound,
    MethodNotAllowed,
    UnsupportedMediaType,
)
from service.routes import api
from service.models import DataValidationError
from . import status


######################################################################
# Error Handlers
######################################################################


# For custom exceptions, use Flask-RESTX's @api.errorhandler
@api.errorhandler(DataValidationError)
def handle_data_validation_error(error):
    """Handles DataValidationError exceptions by returning a 400 response."""
    message = str(error)
    app.logger.error(message)
    return {
        "status": status.HTTP_400_BAD_REQUEST,
        "error": "Bad Request",
        "message": message,
    }, status.HTTP_400_BAD_REQUEST


@api.errorhandler(Exception)
def handle_unexpected_exceptions(error):
    """Handles all uncaught exceptions by returning a 500 response."""
    app.logger.error(f"Internal Server Error: {error}")
    return {
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "error": "Internal Server Error",
        "message": "An unexpected error occurred.",
    }, status.HTTP_500_INTERNAL_SERVER_ERROR


######################################################################
# Standard HTTP Code Handlers — use @app.errorhandler for integers
######################################################################


@app.errorhandler(NotFound)
def not_found(error):
    """Handles 404 Not Found"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=404,
            error="Not Found",
            message=message,
        ),
        404,
    )


@app.errorhandler(MethodNotAllowed)
def method_not_allowed(error):
    """Handles 405 Method Not Allowed"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=405,
            error="Method Not Allowed",
            message=message,
        ),
        405,
    )


@app.errorhandler(UnsupportedMediaType)
def unsupported_media_type(error):
    """Handles 415 Unsupported Media Type"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=415,
            error="Unsupported Media Type",
            message=message,
        ),
        415,
    )
