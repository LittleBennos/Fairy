"""
Security configuration and middleware for production deployment.
Implements defense-in-depth security controls.
"""

import os
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis)
request_counts = defaultdict(lambda: {'count': 0, 'window_start': datetime.now()})


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    Implements OWASP recommended security headers.
    """

    def process_response(self, request, response):
        # Content Security Policy - Prevent XSS
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response['Content-Security-Policy'] = csp

        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), '
            'accelerometer=(), gyroscope=()'
        )

        # HSTS for production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = (
                f'max-age={settings.SECURE_HSTS_SECONDS}; '
                'includeSubDomains; preload'
            )

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Implement rate limiting to prevent abuse and DDoS attacks.
    """

    def process_request(self, request):
        # Skip rate limiting for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None

        # Get client identifier (IP + User if authenticated)
        client_id = self._get_client_id(request)

        # Check rate limit
        if self._is_rate_limited(client_id, request):
            logger.warning(f"Rate limit exceeded for {client_id} on {request.path}")
            return HttpResponseForbidden(
                json.dumps({'error': 'Rate limit exceeded. Please try again later.'}),
                content_type='application/json'
            )

        return None

    def _get_client_id(self, request):
        """Get unique client identifier."""
        ip = self._get_client_ip(request)
        if request.user.is_authenticated:
            return f"{ip}:{request.user.id}"
        return ip

    def _get_client_ip(self, request):
        """Get client's real IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _is_rate_limited(self, client_id, request):
        """Check if client has exceeded rate limit."""
        now = datetime.now()
        window_duration = timedelta(hours=1)

        # Determine rate limit based on endpoint and user type
        if '/auth/login' in request.path:
            max_requests = 3  # 3 login attempts per minute
            window_duration = timedelta(minutes=1)
        elif '/auth/register' in request.path:
            max_requests = 3  # 3 registrations per hour
            window_duration = timedelta(hours=1)
        elif request.user.is_authenticated:
            max_requests = 100  # 100 requests per hour for authenticated users
        else:
            max_requests = 20  # 20 requests per hour for anonymous users

        # Check and update request count
        client_data = request_counts[client_id]
        if now - client_data['window_start'] > window_duration:
            # Reset window
            client_data['count'] = 1
            client_data['window_start'] = now
            return False

        client_data['count'] += 1
        return client_data['count'] > max_requests


class InputValidationMiddleware(MiddlewareMixin):
    """
    Validate and sanitize input to prevent injection attacks.
    """

    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FIELD_LENGTH = 10000  # Maximum length for any single field

    FORBIDDEN_PATTERNS = [
        '<script', '</script>',  # XSS
        'javascript:', 'data:text/html',  # XSS
        'SELECT', 'UNION', 'DROP', 'INSERT', 'UPDATE', 'DELETE',  # SQL Injection
        '../', '..\\',  # Path traversal
        '\x00', '\r\n',  # Null bytes and CRLF injection
    ]

    def process_request(self, request):
        # Check request size
        if request.META.get('CONTENT_LENGTH'):
            content_length = int(request.META['CONTENT_LENGTH'])
            if content_length > self.MAX_REQUEST_SIZE:
                logger.warning(f"Request too large: {content_length} bytes")
                return HttpResponseForbidden('Request too large')

        # Validate POST data
        if request.method == 'POST' and hasattr(request, 'body'):
            body = request.body.decode('utf-8', errors='ignore')
            if self._contains_forbidden_patterns(body):
                logger.warning(f"Forbidden pattern in request from {self._get_client_ip(request)}")
                return HttpResponseForbidden('Invalid input detected')

        # Validate query parameters
        for key, value in request.GET.items():
            if len(str(value)) > self.MAX_FIELD_LENGTH:
                return HttpResponseForbidden('Field too long')
            if self._contains_forbidden_patterns(str(value)):
                logger.warning(f"Forbidden pattern in query param: {key}")
                return HttpResponseForbidden('Invalid input detected')

        return None

    def _contains_forbidden_patterns(self, text):
        """Check if text contains forbidden patterns."""
        text_upper = text.upper()
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern.upper() in text_upper:
                return True
        return False

    def _get_client_ip(self, request):
        """Get client's real IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Log all data access and modifications for security auditing.
    """

    SENSITIVE_OPERATIONS = [
        'DELETE', 'PUT', 'PATCH', 'POST'
    ]

    SENSITIVE_ENDPOINTS = [
        '/api/users/',
        '/api/students/',
        '/api/guardians/',
        '/api/financial/',
        '/api/auth/',
    ]

    def process_request(self, request):
        """Log incoming requests to sensitive endpoints."""
        if not os.environ.get('ENABLE_AUDIT_LOGGING', '').lower() == 'true':
            return None

        # Check if this is a sensitive operation
        if request.method in self.SENSITIVE_OPERATIONS:
            for endpoint in self.SENSITIVE_ENDPOINTS:
                if request.path.startswith(endpoint):
                    self._log_audit_event(request, 'REQUEST')
                    break

        return None

    def process_response(self, request, response):
        """Log responses from sensitive operations."""
        if not os.environ.get('ENABLE_AUDIT_LOGGING', '').lower() == 'true':
            return response

        # Log sensitive operation responses
        if hasattr(request, '_audit_logged') and response.status_code < 400:
            self._log_audit_event(request, 'RESPONSE', response.status_code)

        return response

    def _log_audit_event(self, request, event_type, status_code=None):
        """Log security audit event."""
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        ip = self._get_client_ip(request)

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user': user,
            'ip': ip,
            'method': request.method,
            'path': request.path,
            'status_code': status_code,
        }

        # Don't log sensitive data like passwords
        if request.method in ['POST', 'PUT', 'PATCH'] and request.path != '/api/auth/login/':
            # Log that data was modified but not the actual data
            log_entry['data_modified'] = True

        logger.info(f"AUDIT: {json.dumps(log_entry)}")

        # Mark request as audit logged
        request._audit_logged = True

    def _get_client_ip(self, request):
        """Get client's real IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Enhance session security with additional controls.
    """

    def process_request(self, request):
        # Force session expiry on browser close
        if request.user.is_authenticated:
            request.session.set_expiry(0 if settings.SESSION_EXPIRE_AT_BROWSER_CLOSE else settings.SESSION_COOKIE_AGE)

        # Regenerate session ID on login to prevent session fixation
        if request.path == '/api/auth/login/' and request.method == 'POST':
            if hasattr(request, 'session') and request.session.session_key:
                request.session.cycle_key()

        return None