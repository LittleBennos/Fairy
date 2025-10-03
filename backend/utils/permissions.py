"""
Custom permission classes for role-based access control.
Implements principle of least privilege for API endpoints.
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)


class IsAdminUser(BasePermission):
    """
    Only allow admin users full access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        is_admin = request.user.role == 'admin' or request.user.is_superuser
        if not is_admin:
            logger.warning(f"Non-admin user {request.user.username} attempted to access admin endpoint: {request.path}")
        return is_admin


class IsStaffOrReadOnly(BasePermission):
    """
    Staff members can modify, others can only read.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for staff
        return request.user.is_staff_member


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission - only owners or admins can access.
    """
    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.is_admin:
            return True

        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'guardian') and hasattr(request.user, 'person'):
            return obj.guardian == request.user.person

        return False


class ParentOnlyOwnData(BasePermission):
    """
    Parents can only access their own and their children's data.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admins and staff have full access
        if request.user.is_staff_member:
            return True

        # Parents can only access specific endpoints
        parent_allowed_endpoints = [
            '/api/auth/me/',
            '/api/auth/logout/',
            '/api/auth/change-password/',
            '/api/students/my-children/',
            '/api/enrollments/my-children/',
            '/api/financial/my-invoices/',
            '/api/financial/my-payments/',
            '/api/classes/schedule/',  # Read-only class schedule
        ]

        # Check if the current path is in allowed endpoints
        for endpoint in parent_allowed_endpoints:
            if request.path.startswith(endpoint):
                return True

        # Log unauthorized access attempt
        if request.user.role == 'parent':
            logger.warning(f"Parent user {request.user.username} attempted unauthorized access to: {request.path}")

        return False

    def has_object_permission(self, request, view, obj):
        # Admin/staff can access everything
        if request.user.is_staff_member:
            return True

        # Parent can only access their own data
        if request.user.role == 'parent':
            # Check various ownership patterns
            if hasattr(obj, 'guardian') and hasattr(request.user, 'person'):
                return obj.guardian == request.user.person
            elif hasattr(obj, 'student') and hasattr(obj.student, 'guardians'):
                return request.user.person in obj.student.guardians.all()
            elif hasattr(obj, 'user'):
                return obj.user == request.user

        return False


class StudentOnlyOwnData(BasePermission):
    """
    Students can only access their own limited data.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admins and staff have full access
        if request.user.is_staff_member:
            return True

        # Students have very limited access
        student_allowed_endpoints = [
            '/api/auth/me/',  # Their own profile
            '/api/auth/logout/',
            '/api/auth/change-password/',
            '/api/classes/my-schedule/',  # Their class schedule
            '/api/enrollments/my-enrollments/',  # Their enrollments only
        ]

        # Check if the current path is in allowed endpoints
        for endpoint in student_allowed_endpoints:
            if request.path.startswith(endpoint):
                # Only allow GET requests for students
                return request.method in permissions.SAFE_METHODS

        # Log unauthorized access attempt
        if request.user.role == 'student':
            logger.warning(f"Student user {request.user.username} attempted unauthorized access to: {request.path}")

        return False


class StrictAPIAccess(BasePermission):
    """
    Main permission class that routes to appropriate permission based on user role.
    Implements strict role-based access control.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        user_role = request.user.role

        # Define role-based endpoint access
        role_permissions = {
            'admin': {
                'allowed_methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'blocked_endpoints': [],  # Admins can access everything
            },
            'staff': {
                'allowed_methods': ['GET', 'POST', 'PUT', 'PATCH'],
                'blocked_endpoints': [
                    '/api/users/delete',  # Can't delete users
                    '/api/financial/delete',  # Can't delete financial records
                ]
            },
            'teacher': {
                'allowed_methods': ['GET', 'POST', 'PUT'],
                'blocked_endpoints': [
                    '/api/users/',  # No user management
                    '/api/financial/',  # No financial access
                    '/api/accounts/',  # No account management
                ]
            },
            'parent': {
                'allowed_methods': ['GET'],  # Read-only access
                'blocked_endpoints': [
                    '/api/users/',  # No user lists
                    '/api/guardians/',  # No guardian lists
                    '/api/students/',  # Only their children via specific endpoint
                    '/api/accounts/',  # No account management
                    '/api/people/',  # No people management
                    '/api/scheduling/',  # No schedule management
                ]
            },
            'student': {
                'allowed_methods': ['GET'],  # Read-only access
                'blocked_endpoints': [
                    '/api/users/',
                    '/api/guardians/',
                    '/api/students/',
                    '/api/accounts/',
                    '/api/people/',
                    '/api/financial/',  # No financial data access
                    '/api/scheduling/',
                ]
            }
        }

        # Default to most restrictive if role not found
        role_config = role_permissions.get(user_role, role_permissions['student'])

        # Check if method is allowed for this role
        if request.method not in role_config['allowed_methods']:
            logger.warning(f"User {request.user.username} ({user_role}) attempted {request.method} on {request.path}")
            return False

        # Check if endpoint is blocked for this role
        for blocked_endpoint in role_config['blocked_endpoints']:
            if request.path.startswith(blocked_endpoint):
                logger.warning(f"User {request.user.username} ({user_role}) blocked from accessing {request.path}")
                return False

        return True


class PublicEndpoint(BasePermission):
    """
    Allow access to truly public endpoints only.
    """
    def has_permission(self, request, view):
        # Only allow specific public endpoints
        public_endpoints = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/csrf/',
            '/api/health/',
            '/api/docs/',
        ]

        for endpoint in public_endpoints:
            if request.path.startswith(endpoint):
                return True

        return False


class SecureFileAccess(BasePermission):
    """
    Restrict file upload/download access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Only staff can upload files
        if request.method == 'POST' and 'file' in request.data:
            if not request.user.is_staff_member:
                logger.warning(f"Non-staff user {request.user.username} attempted file upload")
                return False

        return True

    def has_object_permission(self, request, view, obj):
        # Check file ownership for downloads
        if hasattr(obj, 'uploaded_by'):
            # User can download their own files
            if obj.uploaded_by == request.user:
                return True
            # Staff can download any file
            if request.user.is_staff_member:
                return True

        return False