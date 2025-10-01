"""
Health check views for monitoring
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import time


def health_check(request):
    """
    Basic health check endpoint
    Returns 200 if the service is up
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'fairy-backend',
        'timestamp': int(time.time())
    })


def health_check_detailed(request):
    """
    Detailed health check endpoint
    Checks database and cache connectivity
    """
    health_status = {
        'status': 'healthy',
        'service': 'fairy-backend',
        'timestamp': int(time.time()),
        'checks': {}
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            health_status['checks']['database'] = {
                'status': 'healthy',
                'response_time_ms': 0
            }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }

    # Check cache (Redis)
    try:
        start_time = time.time()
        cache.set('health_check', 'ok', 1)
        cache_value = cache.get('health_check')
        response_time = (time.time() - start_time) * 1000

        if cache_value == 'ok':
            health_status['checks']['cache'] = {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2)
            }
        else:
            health_status['status'] = 'unhealthy'
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'error': 'Cache test failed'
            }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }

    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)