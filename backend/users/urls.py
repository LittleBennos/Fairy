from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserViewSet,
    ChangePasswordView
)
from .auth_views import (
    get_csrf_token,
    cookie_login,
    cookie_logout,
    cookie_refresh,
    current_user
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Cookie-based authentication endpoints
    path('auth/csrf/', get_csrf_token, name='get-csrf-token'),
    path('auth/login/', cookie_login, name='cookie-login'),
    path('auth/logout/', cookie_logout, name='cookie-logout'),
    path('auth/refresh/', cookie_refresh, name='cookie-refresh'),
    path('auth/me/', current_user, name='current-user'),

    # JWT token authentication endpoints (for API access)
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),

    # User management endpoints
    path('', include(router.urls)),
]
