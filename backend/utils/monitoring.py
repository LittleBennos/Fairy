"""
API Security Monitoring and Anomaly Detection for 2025 threats.
Implements real-time behavioral monitoring and threat detection.
"""

import logging
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from django.core.cache import cache
from django.conf import settings
from django.core.mail import mail_admins
from django.utils import timezone
import redis

logger = logging.getLogger(__name__)

# Initialize Redis for distributed tracking
try:
    redis_client = redis.from_url(settings.REDIS_URL)
except:
    redis_client = None
    logger.warning("Redis not available, using in-memory cache for monitoring")


class SecurityMonitor:
    """
    Real-time security monitoring and anomaly detection.
    Implements 2025 best practices for API threat detection.
    """

    # Threat detection thresholds
    SUSPICIOUS_PATTERNS = [
        # OWASP API Top 10 2023/2025 patterns
        {'pattern': 'rapid_endpoint_scanning', 'threshold': 20, 'window': 60},  # 20+ different endpoints in 1 minute
        {'pattern': 'credential_stuffing', 'threshold': 5, 'window': 300},  # 5+ failed logins in 5 minutes
        {'pattern': 'data_harvesting', 'threshold': 100, 'window': 600},  # 100+ GET requests in 10 minutes
        {'pattern': 'privilege_escalation', 'threshold': 3, 'window': 60},  # 3+ unauthorized attempts in 1 minute
        {'pattern': 'api_abuse', 'threshold': 50, 'window': 60},  # 50+ requests to same endpoint in 1 minute
        {'pattern': 'zombie_endpoint_access', 'threshold': 1, 'window': 1},  # Any access to deprecated endpoints
    ]

    DEPRECATED_ENDPOINTS = [
        '/api/v1/',  # Old API version
        '/api/test/',  # Test endpoints
        '/api/debug/',  # Debug endpoints
    ]

    def __init__(self):
        self.anomaly_scores = defaultdict(lambda: {'score': 0, 'last_reset': timezone.now()})

    def track_request(self, request, response=None):
        """
        Track and analyze API request for suspicious patterns.
        """
        client_id = self._get_client_identifier(request)
        endpoint = request.path
        method = request.method
        status_code = response.status_code if response else 0

        # Track in Redis for distributed monitoring
        if redis_client:
            self._track_in_redis(client_id, endpoint, method, status_code)
        else:
            self._track_in_memory(client_id, endpoint, method, status_code)

        # Check for anomalies
        anomalies = self._detect_anomalies(client_id, request)

        if anomalies:
            self._handle_anomalies(client_id, anomalies, request)

        # Check for zombie endpoint access
        if self._is_zombie_endpoint(endpoint):
            logger.warning(f"Zombie endpoint accessed: {endpoint} by {client_id}")
            self._alert_security_team(
                f"Deprecated API Endpoint Access",
                f"Client {client_id} accessed deprecated endpoint: {endpoint}"
            )

    def _get_client_identifier(self, request):
        """
        Create unique client identifier combining multiple factors.
        """
        factors = []

        # IP address
        ip = self._get_client_ip(request)
        factors.append(ip)

        # User ID if authenticated
        if request.user and request.user.is_authenticated:
            factors.append(f"user_{request.user.id}")

        # User agent fingerprint
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if user_agent:
            ua_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]
            factors.append(f"ua_{ua_hash}")

        # Session ID if available
        if hasattr(request, 'session') and request.session.session_key:
            factors.append(f"sess_{request.session.session_key[:8]}")

        return ":".join(factors)

    def _get_client_ip(self, request):
        """Get real client IP considering proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

    def _track_in_redis(self, client_id, endpoint, method, status_code):
        """Track request patterns in Redis for distributed monitoring."""
        try:
            now = timezone.now()
            timestamp = now.timestamp()

            # Track endpoint access patterns
            key = f"api_monitor:{client_id}:endpoints"
            redis_client.zadd(key, {endpoint: timestamp})
            redis_client.expire(key, 3600)  # 1 hour expiry

            # Track failed authentications
            if status_code == 401:
                fail_key = f"api_monitor:{client_id}:auth_fails"
                redis_client.incr(fail_key)
                redis_client.expire(fail_key, 300)  # 5 minute expiry

            # Track method distribution
            method_key = f"api_monitor:{client_id}:methods:{method}"
            redis_client.incr(method_key)
            redis_client.expire(method_key, 600)  # 10 minute expiry

        except Exception as e:
            logger.error(f"Redis tracking error: {e}")

    def _track_in_memory(self, client_id, endpoint, method, status_code):
        """Fallback to in-memory tracking if Redis unavailable."""
        cache_key = f"monitor_{client_id}"
        data = cache.get(cache_key, {
            'endpoints': [],
            'auth_fails': 0,
            'methods': defaultdict(int)
        })

        data['endpoints'].append({
            'endpoint': endpoint,
            'timestamp': timezone.now(),
            'method': method
        })

        if status_code == 401:
            data['auth_fails'] += 1

        data['methods'][method] += 1

        # Keep only recent data
        cutoff = timezone.now() - timedelta(minutes=10)
        data['endpoints'] = [
            e for e in data['endpoints']
            if e['timestamp'] > cutoff
        ]

        cache.set(cache_key, data, 600)  # 10 minute cache

    def _detect_anomalies(self, client_id, request):
        """
        Detect anomalous patterns based on 2025 threat intelligence.
        """
        anomalies = []

        if redis_client:
            # Check rapid endpoint scanning
            endpoints_key = f"api_monitor:{client_id}:endpoints"
            unique_endpoints = redis_client.zcard(endpoints_key)

            if unique_endpoints > 20:
                anomalies.append({
                    'type': 'rapid_endpoint_scanning',
                    'severity': 'high',
                    'details': f'Accessed {unique_endpoints} different endpoints'
                })

            # Check credential stuffing
            fail_key = f"api_monitor:{client_id}:auth_fails"
            auth_fails = redis_client.get(fail_key)

            if auth_fails and int(auth_fails) >= 5:
                anomalies.append({
                    'type': 'credential_stuffing',
                    'severity': 'critical',
                    'details': f'{auth_fails} failed authentication attempts'
                })

            # Check data harvesting patterns
            get_key = f"api_monitor:{client_id}:methods:GET"
            get_count = redis_client.get(get_key)

            if get_count and int(get_count) > 100:
                anomalies.append({
                    'type': 'data_harvesting',
                    'severity': 'medium',
                    'details': f'{get_count} GET requests in short period'
                })

        # Check for privilege escalation attempts
        if request.user and request.user.is_authenticated:
            if request.user.role in ['parent', 'student']:
                admin_patterns = ['/api/users/', '/api/financial/', '/api/accounts/']
                if any(request.path.startswith(p) for p in admin_patterns):
                    anomalies.append({
                        'type': 'privilege_escalation',
                        'severity': 'critical',
                        'details': f'{request.user.role} accessing admin endpoint'
                    })

        return anomalies

    def _is_zombie_endpoint(self, endpoint):
        """Check if endpoint is deprecated/zombie."""
        for deprecated in self.DEPRECATED_ENDPOINTS:
            if endpoint.startswith(deprecated):
                return True
        return False

    def _handle_anomalies(self, client_id, anomalies, request):
        """
        Handle detected anomalies based on severity.
        """
        # Calculate cumulative anomaly score
        total_severity = 0
        severity_scores = {'low': 1, 'medium': 3, 'high': 5, 'critical': 10}

        for anomaly in anomalies:
            severity = anomaly.get('severity', 'low')
            total_severity += severity_scores.get(severity, 1)

            # Log the anomaly
            logger.warning(f"ANOMALY DETECTED - Client: {client_id}, Type: {anomaly['type']}, Details: {anomaly['details']}")

        # Update anomaly score for client
        self.anomaly_scores[client_id]['score'] += total_severity

        # Take action based on score
        client_score = self.anomaly_scores[client_id]['score']

        if client_score >= 20:
            # Block the client temporarily
            self._block_client(client_id, duration=3600)  # 1 hour
            self._alert_security_team(
                "Critical Security Threat Detected",
                f"Client {client_id} blocked due to suspicious activity. Score: {client_score}\nAnomalies: {json.dumps(anomalies, indent=2)}"
            )
        elif client_score >= 10:
            # Alert but don't block
            self._alert_security_team(
                "High Risk Activity Detected",
                f"Client {client_id} showing suspicious patterns. Score: {client_score}\nAnomalies: {json.dumps(anomalies, indent=2)}"
            )

    def _block_client(self, client_id, duration):
        """
        Temporarily block a client.
        """
        block_key = f"blocked_client:{client_id}"

        if redis_client:
            redis_client.setex(block_key, duration, "blocked")
        else:
            cache.set(block_key, "blocked", duration)

        logger.critical(f"CLIENT BLOCKED: {client_id} for {duration} seconds")

    def is_client_blocked(self, request):
        """
        Check if client is currently blocked.
        """
        client_id = self._get_client_identifier(request)
        block_key = f"blocked_client:{client_id}"

        if redis_client:
            return redis_client.get(block_key) is not None
        else:
            return cache.get(block_key) is not None

    def _alert_security_team(self, subject, message):
        """
        Send security alert to administrators.
        """
        try:
            if settings.DEBUG:
                logger.critical(f"SECURITY ALERT: {subject}\n{message}")
            else:
                mail_admins(subject, message, fail_silently=True)
        except Exception as e:
            logger.error(f"Failed to send security alert: {e}")


class APIInventoryManager:
    """
    Manages API inventory to prevent shadow/zombie APIs.
    2025 best practice: Track all active endpoints.
    """

    def __init__(self):
        self.documented_endpoints = set()
        self.discovered_endpoints = set()
        self.last_audit = None

    def discover_endpoints(self):
        """
        Dynamically discover all API endpoints.
        """
        from django.urls import get_resolver
        from django.urls.resolvers import URLPattern, URLResolver

        def extract_patterns(resolver, prefix=''):
            patterns = []
            for pattern in resolver.url_patterns:
                if isinstance(pattern, URLPattern):
                    path = prefix + str(pattern.pattern)
                    patterns.append(path)
                elif isinstance(pattern, URLResolver):
                    sub_prefix = prefix + str(pattern.pattern)
                    patterns.extend(extract_patterns(pattern, sub_prefix))
            return patterns

        resolver = get_resolver()
        self.discovered_endpoints = set(extract_patterns(resolver))
        self.last_audit = timezone.now()

        return self.discovered_endpoints

    def find_shadow_apis(self):
        """
        Identify shadow APIs (undocumented but active).
        """
        if not self.discovered_endpoints:
            self.discover_endpoints()

        shadow_apis = self.discovered_endpoints - self.documented_endpoints

        if shadow_apis:
            logger.warning(f"Shadow APIs detected: {shadow_apis}")

        return shadow_apis

    def audit_api_inventory(self):
        """
        Perform comprehensive API inventory audit.
        """
        audit_report = {
            'timestamp': timezone.now().isoformat(),
            'total_endpoints': len(self.discovered_endpoints),
            'documented_endpoints': len(self.documented_endpoints),
            'shadow_apis': list(self.find_shadow_apis()),
            'deprecated_apis': SecurityMonitor.DEPRECATED_ENDPOINTS,
        }

        # Log audit report
        logger.info(f"API Inventory Audit: {json.dumps(audit_report, indent=2)}")

        return audit_report


# Global monitor instance
security_monitor = SecurityMonitor()
api_inventory = APIInventoryManager()