from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GenreViewSet, ClassTypeViewSet, EvaluationViewSet,
    TermViewSet, ClassInstanceViewSet, EnrollmentViewSet, AttendanceRecordViewSet
)

router = DefaultRouter()
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'class-types', ClassTypeViewSet, basename='classtype')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')
router.register(r'terms', TermViewSet, basename='term')
router.register(r'classes', ClassInstanceViewSet, basename='class')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]