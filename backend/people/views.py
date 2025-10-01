from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import Person
from .serializers import PersonSerializer, PersonListSerializer, PersonCreateSerializer


class PersonFilter(filters.FilterSet):
    """Filter for Person queries"""
    is_active = filters.BooleanFilter()
    has_user = filters.BooleanFilter(field_name='user', lookup_expr='isnull', exclude=True)

    class Meta:
        model = Person
        fields = ['is_active']


class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing people.
    People are the base entity for all individuals in the system.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PersonFilter
    search_fields = ['given_name', 'family_name', 'email', 'person_code', 'preferred_name']
    ordering_fields = ['family_name', 'given_name', 'created_at']
    ordering = ['family_name', 'given_name']

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return PersonListSerializer
        elif self.action == 'create':
            return PersonCreateSerializer
        return PersonSerializer

    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """Get all roles associated with this person"""
        person = self.get_object()
        roles = []

        # Check for each role type
        if hasattr(person, 'student'):
            roles.append({
                'type': 'student',
                'id': person.student.id,
                'status': person.student.status,
            })

        if hasattr(person, 'guardian'):
            roles.append({
                'type': 'guardian',
                'id': person.guardian.id,
            })

        if hasattr(person, 'billing_contact'):
            roles.append({
                'type': 'billing_contact',
                'id': person.billing_contact.id,
            })

        if hasattr(person, 'staff'):
            roles.append({
                'type': 'staff',
                'id': person.staff.id,
                'staff_type': person.staff.staff_type,
                'is_active': person.staff.is_active,
            })

        return Response({'roles': roles})

    @action(detail=True, methods=['post'])
    def create_user_account(self, request, pk=None):
        """Create a user account for this person to access the portal"""
        person = self.get_object()

        if person.user:
            return Response(
                {'error': 'This person already has a user account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get username and password from request
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role', 'parent')  # default to parent role

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from users.models import User

        try:
            # Create user account
            user = User.objects.create_user(
                username=username,
                password=password,
                email=person.email,
                first_name=person.given_name,
                last_name=person.family_name,
                role=role,
                person=person
            )

            # Update person with user link
            person.user = user
            person.save()

            from users.serializers import UserSerializer
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
