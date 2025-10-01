"""
Custom authentication views for cookie-based JWT authentication.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from utils.authentication import set_jwt_cookies, clear_jwt_cookies
from django.middleware.csrf import get_token
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class LoginRateThrottle(AnonRateThrottle):
    """Custom throttle for login attempts."""
    scope = 'login'  # Uses 'login' rate from settings


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Get CSRF token for the frontend.
    The @ensure_csrf_cookie decorator ensures a CSRF cookie is set.
    """
    response = Response({
        'detail': 'CSRF cookie set',
        'csrfToken': get_token(request)
    })

    # Also set CSRF token as httpOnly=False cookie for JavaScript access
    response.set_cookie(
        'csrftoken',
        get_token(request),
        max_age=60 * 60 * 24,  # 24 hours
        httponly=False,  # Must be accessible by JavaScript
        secure=not settings.DEBUG,
        samesite='Lax'
    )

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def cookie_login(request):
    """
    Login endpoint that sets JWT tokens as httpOnly cookies.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Authenticate user
    user = authenticate(username=username, password=password)

    if user is None:
        logger.warning(f"Failed login attempt for username: {username}")
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Create response with user info
    response = Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        },
        'message': 'Login successful'
    }, status=status.HTTP_200_OK)

    # Set JWT cookies
    response = set_jwt_cookies(response, user)

    # Log successful login
    logger.info(f"Successful login for user: {username}")

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cookie_logout(request):
    """
    Logout endpoint that clears JWT cookies.
    """
    # Get refresh token from cookie to blacklist it
    refresh_token = request.COOKIES.get('refresh_token')

    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            # Token is already invalid or blacklisted
            pass
        except Exception as e:
            logger.error(f"Error blacklisting token during logout: {str(e)}")

    # Create response
    response = Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)

    # Clear JWT cookies
    response = clear_jwt_cookies(response)

    logger.info(f"User {request.user.username} logged out successfully")

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def cookie_refresh(request):
    """
    Refresh endpoint that uses refresh token from httpOnly cookie.
    """
    refresh_token = request.COOKIES.get('refresh_token')

    if not refresh_token:
        return Response(
            {'error': 'Refresh token not found'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        # Create new access token from refresh token
        token = RefreshToken(refresh_token)
        access_token = token.access_token

        # Create response
        response = Response({
            'message': 'Token refreshed successfully'
        }, status=status.HTTP_200_OK)

        # Update access token cookie
        from django.conf import settings
        response.set_cookie(
            key='access_token',
            value=str(access_token),
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            path='/api/'
        )

        return response

    except TokenError as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        return Response(
            {'error': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get current authenticated user information.
    """
    user = request.user
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
        }
    }, status=status.HTTP_200_OK)