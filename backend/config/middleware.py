"""
Custom middleware for security headers and rate limiting
"""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
import logging
import os
import time

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""

    def process_response(self, request, response):
        # Content Security Policy - Stricter policy for production
        if not settings.DEBUG:
            # Use nonce-based CSP for inline scripts/styles in production
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' https://cdn.jsdelivr.net; "
                "style-src 'self' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "img-src 'self' data: https:; "
                "connect-src 'self' " + os.environ.get('VITE_API_URL', '') + "; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
            # Report-Only header for testing stricter CSP
            response['Content-Security-Policy-Report-Only'] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "report-uri /api/csp-report/"
            )

        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), '
            'gyroscope=(), magnetometer=(), microphone=(), '
            'payment=(), usb=()'
        )

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """Global rate limiting middleware for API endpoints"""

    def process_request(self, request):
        # Skip rate limiting in development unless explicitly enabled
        if settings.DEBUG and os.environ.get('RATELIMIT_ENABLE', 'False').lower() != 'true':
            return None

        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None

        # Skip for static files and media
        if request.path.startswith(('/static/', '/media/')):
            return None

        # Get client IP
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR')

        try:
            # Rate limiting: 100 requests per minute per IP
            cache_key = f'api_rate_limit_{client_ip}'
            minute_key = f'{cache_key}_{int(time.time() // 60)}'
            cache_timeout = int(os.environ.get('RATELIMIT_CACHE_TIMEOUT', 60))

            requests_count = cache.get(minute_key, 0)
            max_requests = int(os.environ.get('RATELIMIT_API_CALLS', 100))

            if requests_count >= max_requests:
                logger.warning(f"API rate limit exceeded for IP: {client_ip}")
                return HttpResponse(
                    'Too many requests. Please slow down.',
                    status=429,
                    content_type='text/plain'
                )

            # Increment counter
            cache.set(minute_key, requests_count + 1, cache_timeout)

        except Exception as e:
            # Log error but don't block the request if Redis is down
            logger.error(f"Rate limiting error: {str(e)}", exc_info=True)
            # Continue processing the request without rate limiting

        return None

