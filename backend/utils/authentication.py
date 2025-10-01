"""
Custom authentication classes for httpOnly cookie-based JWT authentication.
Provides better security than localStorage/sessionStorage for token storage.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import exceptions


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication using httpOnly cookies instead of headers.
    This prevents XSS attacks from accessing the tokens.
    """

    def authenticate(self, request):
        """
        Authenticate the request using JWT token from httpOnly cookie.
        """
        # Get the access token from the cookie
        raw_token = request.COOKIES.get('access_token', None)

        if raw_token is None:
            return None

        # Validate the token
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # Enforce CSRF protection for cookie-based auth
        self.enforce_csrf(request)

        return (user, validated_token)

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for cookie-based authentication.
        """
        # Skip CSRF check for safe methods
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return

        # Get CSRF token from request headers
        csrf_token = None

        # Check for CSRF token in headers (X-CSRFToken)
        if 'HTTP_X_CSRFTOKEN' in request.META:
            csrf_token = request.META['HTTP_X_CSRFTOKEN']
        elif 'X-CSRFToken' in request.headers:
            csrf_token = request.headers['X-CSRFToken']

        # Get the expected token from cookies
        expected_token = request.COOKIES.get('csrftoken', '')

        # Validate CSRF token
        if not csrf_token or csrf_token != expected_token:
            raise exceptions.PermissionDenied('CSRF validation failed')


def set_jwt_cookies(response, user):
    """
    Set JWT tokens as httpOnly cookies in the response.

    Args:
        response: Django HttpResponse object
        user: User instance
    """
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    # Set access token cookie
    response.set_cookie(
        key='access_token',
        value=str(access_token),
        max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite='Lax',
        path='/api/'  # Restrict to API paths
    )

    # Set refresh token cookie
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        path='/api/auth/'  # More restrictive path for refresh token
    )

    return response


def clear_jwt_cookies(response):
    """
    Clear JWT cookies from the response (for logout).

    Args:
        response: Django HttpResponse object
    """
    response.delete_cookie('access_token', path='/api/')
    response.delete_cookie('refresh_token', path='/api/auth/')
    return response