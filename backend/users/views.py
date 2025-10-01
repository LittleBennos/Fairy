from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    UserListSerializer,
    RegisterSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class RegisterRateThrottle(AnonRateThrottle):
    """Custom throttle for registration attempts."""
    scope = 'register'  # Uses 'register' rate from settings


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Public endpoint - no authentication required.
    Rate limited to prevent abuse.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    API endpoint for user login.
    Returns JWT access and refresh tokens.
    """
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """
    API endpoint for user logout.
    Blacklists the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management.
    Provides CRUD operations for users with role-based filtering.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = User.objects.all()

        # Parents can only see their own account
        if user.is_parent_user and not user.is_staff_member:
            return queryset.filter(id=user.id)

        # Staff can see all non-admin users
        if user.is_staff_member and not user.is_admin:
            return queryset.exclude(role='admin')

        # Admins can see everyone
        return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint for changing user password.
    Requires old password for verification.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'Password updated successfully'
        }, status=status.HTTP_200_OK)
