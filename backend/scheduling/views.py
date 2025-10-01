from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Genre, ClassType, Evaluation, Term, ClassInstance, Enrollment, AttendanceRecord
from .serializers import (
    GenreSerializer, GenreListSerializer,
    ClassTypeSerializer, ClassTypeListSerializer,
    EvaluationSerializer, EvaluationListSerializer,
    TermSerializer, TermListSerializer,
    ClassInstanceSerializer, ClassInstanceListSerializer,
    EnrollmentSerializer, EnrollmentListSerializer,
    AttendanceRecordSerializer, AttendanceRecordListSerializer
)


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet for Genre CRUD operations"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return GenreListSerializer
        return GenreSerializer


class ClassTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for ClassType CRUD operations"""
    queryset = ClassType.objects.select_related('genre').all()
    serializer_class = ClassTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'level', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'genre', 'level', 'price_per_term', 'created_at']
    ordering = ['genre', 'level', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClassTypeListSerializer
        return ClassTypeSerializer


class EvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet for Evaluation CRUD operations"""
    queryset = Evaluation.objects.select_related('student__person', 'genre', 'evaluated_by__person').all()
    serializer_class = EvaluationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'genre', 'level_achieved', 'evaluated_by']
    search_fields = ['student__person__given_name', 'student__person__family_name', 'genre__name', 'notes']
    ordering_fields = ['evaluation_date', 'level_achieved', 'created_at']
    ordering = ['-evaluation_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return EvaluationListSerializer
        return EvaluationSerializer


class TermViewSet(viewsets.ModelViewSet):
    """ViewSet for Term CRUD operations"""
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return TermListSerializer
        return TermSerializer


class ClassInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet for ClassInstance CRUD operations"""
    queryset = ClassInstance.objects.select_related('class_type__genre', 'term', 'teacher__person').all()
    serializer_class = ClassInstanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_type', 'term', 'teacher', 'day_of_week', 'status']
    search_fields = ['class_type__name', 'term__name', 'room']
    ordering_fields = ['day_of_week', 'start_time', 'created_at']
    ordering = ['term', 'day_of_week', 'start_time']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClassInstanceListSerializer
        return ClassInstanceSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Enrollment CRUD operations"""
    queryset = Enrollment.objects.select_related(
        'account__student__person',
        'account__guardian__person',
        'account__billing_contact__person',
        'class_instance__class_type__genre',
        'class_instance__term'
    ).all()
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account', 'class_instance', 'status']
    search_fields = [
        'account__student__person__given_name',
        'account__student__person__family_name',
        'account__account_code',
        'class_instance__class_type__name'
    ]
    ordering_fields = ['enrollment_date', 'status', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return EnrollmentListSerializer
        return EnrollmentSerializer


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for AttendanceRecord CRUD operations"""
    queryset = AttendanceRecord.objects.select_related(
        'student__person',
        'class_instance__class_type__genre',
        'class_instance__term',
        'enrollment__account',
        'marked_by__person'
    ).all()
    serializer_class = AttendanceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'class_instance', 'enrollment', 'status', 'date', 'marked_by']
    search_fields = [
        'student__person__given_name',
        'student__person__family_name',
        'class_instance__class_type__name',
        'notes'
    ]
    ordering_fields = ['date', 'status', 'marked_at', 'created_at']
    ordering = ['-date', 'class_instance', 'student']

    def get_serializer_class(self):
        if self.action == 'list':
            return AttendanceRecordListSerializer
        return AttendanceRecordSerializer

    def perform_create(self, serializer):
        """Automatically set marked_by to current staff member"""
        # Assuming request.user has a related staff object
        if hasattr(self.request.user, 'person') and hasattr(self.request.user.person, 'staff'):
            serializer.save(marked_by=self.request.user.person.staff)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """Automatically update marked_by to current staff member"""
        # Assuming request.user has a related staff object
        if hasattr(self.request.user, 'person') and hasattr(self.request.user.person, 'staff'):
            serializer.save(marked_by=self.request.user.person.staff)
        else:
            serializer.save()
