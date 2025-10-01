"""
Custom error handlers and exception classes for the application.
Prevents sensitive information leakage in production.
"""

import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.defaults import (
    bad_request, permission_denied, page_not_found, server_error
)
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Logs detailed errors server-side but returns generic messages to clients in production.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Log the actual error details
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            exc_info=True,
            extra={
                'request': context.get('request'),
                'view': context.get('view'),
            }
        )

        # In production, sanitize error messages
        if not settings.DEBUG:
            # Map specific error types to generic messages
            error_messages = {
                400: "Invalid request. Please check your input.",
                401: "Authentication required. Please log in.",
                403: "You don't have permission to perform this action.",
                404: "The requested resource was not found.",
                405: "Method not allowed for this endpoint.",
                429: "Too many requests. Please try again later.",
                500: "An error occurred while processing your request.",
                502: "Service temporarily unavailable.",
                503: "Service temporarily unavailable.",
            }

            # Get generic message or default
            status_code = response.status_code
            generic_message = error_messages.get(
                status_code,
                "An error occurred while processing your request."
            )

            # Replace detailed error with generic message
            response.data = {
                'error': generic_message,
                'status_code': status_code
            }

            # Remove field-specific errors in production
            if 'detail' in response.data:
                del response.data['detail']

    return response


def handle_400(request, exception=None):
    """Handle 400 Bad Request errors"""
    if settings.DEBUG:
        return bad_request(request, exception)

    logger.error(f"400 Bad Request: {request.path}", exc_info=True)
    return JsonResponse({
        'error': 'Invalid request. Please check your input.',
        'status_code': 400
    }, status=400)


def handle_403(request, exception=None):
    """Handle 403 Permission Denied errors"""
    if settings.DEBUG:
        return permission_denied(request, exception)

    logger.warning(f"403 Permission Denied: {request.path} by {request.user}")
    return JsonResponse({
        'error': "You don't have permission to perform this action.",
        'status_code': 403
    }, status=403)


def handle_404(request, exception=None):
    """Handle 404 Not Found errors"""
    if settings.DEBUG:
        return page_not_found(request, exception)

    logger.info(f"404 Not Found: {request.path}")
    return JsonResponse({
        'error': 'The requested resource was not found.',
        'status_code': 404
    }, status=404)


def handle_500(request):
    """Handle 500 Internal Server errors"""
    if settings.DEBUG:
        return server_error(request)

    logger.error(f"500 Internal Server Error: {request.path}", exc_info=True)
    return JsonResponse({
        'error': 'An error occurred while processing your request.',
        'status_code': 500
    }, status=500)


class SafeValidationError(Exception):
    """
    Custom validation error that provides safe messages to users.
    Use this for business logic errors that should be shown to users.
    """
    def __init__(self, message, code=None):
        self.message = message
        self.code = code or 'validation_error'
        super().__init__(self.message)