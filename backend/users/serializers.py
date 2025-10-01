from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    full_name = serializers.ReadOnlyField()
    is_admin = serializers.ReadOnlyField()
    is_staff_member = serializers.ReadOnlyField()
    is_parent_user = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'person', 'is_active', 'is_admin',
            'is_staff_member', 'is_parent_user', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user lists"""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'role', 'is_active', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role', 'phone']

    def validate(self, attrs):
        """Validate passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'Password fields must match'
            })
        return attrs

    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists')
        return value

    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint"""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Validate new passwords match"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password': 'Password fields must match'
            })
        return attrs

    def validate_old_password(self, value):
        """Validate old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value

    def save(self, **kwargs):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
