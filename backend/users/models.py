from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Supports role-based access control for staff and parents.
    """

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff Member'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent/Guardian'),
        ('guardian', 'Guardian'),
        ('student', 'Student'),
    ]

    # Additional fields
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff',
        help_text="User's role in the system"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Link to Person model if this user represents a person in the system
    # (e.g., a parent user linked to a Guardian person, or staff user linked to Staff person)
    person = models.OneToOneField(
        'people.Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_account',
        help_text="Link to Person record if applicable"
    )

    # Account status
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active"
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        """Return user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin' or self.is_superuser

    @property
    def is_staff_member(self):
        """Check if user is staff or teacher"""
        return self.role in ['admin', 'staff', 'teacher'] or self.is_superuser

    @property
    def is_parent_user(self):
        """Check if user is a parent"""
        return self.role == 'parent'
